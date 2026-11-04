from __future__ import annotations

from dataclasses import dataclass
from math import asin, cos, radians, sin, sqrt
from pathlib import Path
from types import MappingProxyType
from typing import IO, Mapping
import xml.etree.ElementTree as ET

from accesstrace.routing import ACCESSIBILITY_TAGS, RouteEdge


SUPPORTED_HIGHWAYS = frozenset({"footway", "path", "pedestrian", "steps"})
EARTH_RADIUS_M = 6_371_000.0


@dataclass(frozen=True)
class Place:
    osm_id: str
    name: str
    lat: float
    lon: float
    nearest_node_id: str


@dataclass(frozen=True)
class OsmGraph:
    edges: tuple[RouteEdge, ...]
    places: tuple[Place, ...]
    coordinates: Mapping[str, tuple[float, float]]


@dataclass(frozen=True)
class _Node:
    lat: float
    lon: float
    tags: Mapping[str, str]


def _tags(element: ET.Element) -> dict[str, str]:
    return {tag.attrib["k"]: tag.attrib["v"] for tag in element.findall("tag")}


def _distance_m(first: tuple[float, float], second: tuple[float, float]) -> float:
    lat1, lon1 = map(radians, first)
    lat2, lon2 = map(radians, second)
    delta_lat = lat2 - lat1
    delta_lon = lon2 - lon1
    value = sin(delta_lat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(delta_lon / 2) ** 2
    return 2 * EARTH_RADIUS_M * asin(sqrt(value))


def _combined_edge_tags(
    way_tags: Mapping[str, str],
    first: _Node,
    second: _Node,
) -> dict[str, str]:
    combined = {
        key: value
        for key, value in way_tags.items()
        if key == "highway" or key in ACCESSIBILITY_TAGS
    }
    endpoint_tags = (first.tags, second.tags)

    for key in ACCESSIBILITY_TAGS:
        values = [tags[key] for tags in endpoint_tags if key in tags]
        if not values or key in combined:
            continue
        if key == "kerb" and "raised" in values:
            combined[key] = "raised"
        elif key == "wheelchair" and "no" in values:
            combined[key] = "no"
        else:
            combined[key] = values[0]

    return combined


def _parse_nodes(root: ET.Element) -> dict[str, _Node]:
    nodes = {}
    for element in root.findall("node"):
        node_id = element.attrib["id"]
        nodes[node_id] = _Node(
            lat=float(element.attrib["lat"]),
            lon=float(element.attrib["lon"]),
            tags=MappingProxyType(_tags(element)),
        )
    return nodes


def _require_nodes(node_ids: list[str], nodes: Mapping[str, _Node], way_id: str) -> None:
    for node_id in node_ids:
        if node_id not in nodes:
            raise ValueError(f"OSM way {way_id} references missing node {node_id}")


def _pedestrian_edges(root: ET.Element, nodes: Mapping[str, _Node]) -> tuple[RouteEdge, ...]:
    edges = []
    for way in root.findall("way"):
        tags = _tags(way)
        if tags.get("highway") not in SUPPORTED_HIGHWAYS:
            continue
        node_ids = [item.attrib["ref"] for item in way.findall("nd")]
        _require_nodes(node_ids, nodes, way.attrib["id"])
        for start, end in zip(node_ids, node_ids[1:]):
            distance = _distance_m(
                (nodes[start].lat, nodes[start].lon),
                (nodes[end].lat, nodes[end].lon),
            )
            if distance == 0:
                continue
            edges.append(
                RouteEdge(
                    start=start,
                    end=end,
                    distance_m=distance,
                    tags=_combined_edge_tags(tags, nodes[start], nodes[end]),
                )
            )
    return tuple(edges)


def _named_places(
    root: ET.Element,
    nodes: Mapping[str, _Node],
    network_node_ids: frozenset[str],
) -> tuple[Place, ...]:
    places = []
    for way in root.findall("way"):
        tags = _tags(way)
        if not tags.get("name") or not (tags.get("building") or tags.get("amenity")):
            continue
        node_ids = [item.attrib["ref"] for item in way.findall("nd")]
        _require_nodes(node_ids, nodes, way.attrib["id"])
        lat = sum(nodes[node_id].lat for node_id in node_ids) / len(node_ids)
        lon = sum(nodes[node_id].lon for node_id in node_ids) / len(node_ids)
        nearest = min(
            network_node_ids,
            key=lambda node_id: (_distance_m((lat, lon), (nodes[node_id].lat, nodes[node_id].lon)), node_id),
        )
        places.append(
            Place(
                osm_id=way.attrib["id"],
                name=tags["name"],
                lat=lat,
                lon=lon,
                nearest_node_id=nearest,
            )
        )
    return tuple(sorted(places, key=lambda place: (place.name.casefold(), place.osm_id)))


def parse_osm(source: str | Path | IO[str]) -> OsmGraph:
    """Parse an OSM XML extract into a deterministic outdoor pedestrian graph."""
    root = ET.parse(source).getroot()
    nodes = _parse_nodes(root)
    edges = _pedestrian_edges(root, nodes)
    if not edges:
        raise ValueError("No supported pedestrian network found in OSM data")

    network_node_ids = frozenset(
        node_id
        for edge in edges
        for node_id in (edge.start, edge.end)
    )
    coordinates = MappingProxyType(
        {
            node_id: (nodes[node_id].lat, nodes[node_id].lon)
            for node_id in sorted(network_node_ids)
        }
    )
    return OsmGraph(
        edges=edges,
        places=_named_places(root, nodes, network_node_ids),
        coordinates=coordinates,
    )
