from __future__ import annotations

from dataclasses import dataclass, field
from heapq import heappop, heappush
from types import MappingProxyType
from typing import Iterable, Mapping


ACCESSIBILITY_TAGS = frozenset(
    {
        "wheelchair",
        "kerb",
        "surface",
        "incline",
        "smoothness",
        "ramp:wheelchair",
    }
)


class NoRouteError(ValueError):
    """Raised when every candidate path contains a known blocker."""


def _edge_id(start: str, end: str) -> str:
    return ":".join(sorted((start, end)))


@dataclass(frozen=True)
class RouteEdge:
    start: str
    end: str
    distance_m: float
    tags: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.start or not self.end:
            raise ValueError("Route edge endpoints must be non-empty")
        if self.distance_m <= 0:
            raise ValueError("Route edge distance must be positive")
        object.__setattr__(self, "tags", MappingProxyType(dict(self.tags)))

    @property
    def edge_id(self) -> str:
        return _edge_id(self.start, self.end)


@dataclass(frozen=True)
class CandidateRoute:
    nodes: tuple[str, ...]
    distance_m: float
    evidence_coverage: float
    unknown_edges: tuple[str, ...]
    excluded_edges: tuple[str, ...]


def _normalized_barriers(active_barriers: Iterable[str]) -> frozenset[str]:
    normalized = set()
    for barrier in active_barriers:
        parts = barrier.split(":", 1)
        normalized.add(_edge_id(*parts) if len(parts) == 2 else barrier)
    return frozenset(normalized)


def _is_blocked(edge: RouteEdge, active_barriers: frozenset[str]) -> bool:
    if edge.edge_id in active_barriers:
        return True
    if edge.tags.get("wheelchair") == "no":
        return True
    if edge.tags.get("kerb") == "raised":
        return True
    return edge.tags.get("highway") == "steps" and edge.tags.get("ramp:wheelchair") not in {
        "yes",
        "designated",
    }


def _has_accessibility_evidence(edge: RouteEdge) -> bool:
    return bool(ACCESSIBILITY_TAGS.intersection(edge.tags))


def find_candidate_route(
    edges: Iterable[RouteEdge],
    start: str,
    end: str,
    *,
    active_barriers: Iterable[str] = (),
) -> CandidateRoute:
    """Return the shortest unblocked candidate route and its evidence coverage."""
    barriers = _normalized_barriers(active_barriers)
    adjacency: dict[str, list[tuple[str, RouteEdge]]] = {}
    excluded: set[str] = set()

    for edge in tuple(edges):
        if _is_blocked(edge, barriers):
            excluded.add(edge.edge_id)
            continue
        adjacency.setdefault(edge.start, []).append((edge.end, edge))
        adjacency.setdefault(edge.end, []).append((edge.start, edge))

    queue: list[tuple[float, str]] = [(0.0, start)]
    distances = {start: 0.0}
    previous: dict[str, tuple[str, RouteEdge]] = {}

    while queue:
        distance, node = heappop(queue)
        if distance != distances.get(node):
            continue
        if node == end:
            break
        for neighbor, edge in sorted(adjacency.get(node, ()), key=lambda item: (item[0], item[1].edge_id)):
            candidate = distance + edge.distance_m
            if candidate < distances.get(neighbor, float("inf")):
                distances[neighbor] = candidate
                previous[neighbor] = (node, edge)
                heappush(queue, (candidate, neighbor))

    if end not in distances:
        raise NoRouteError(f"No candidate route from {start!r} to {end!r}")

    nodes = [end]
    route_edges: list[RouteEdge] = []
    current = end
    while current != start:
        parent, edge = previous[current]
        nodes.append(parent)
        route_edges.append(edge)
        current = parent
    nodes.reverse()
    route_edges.reverse()

    unknown = tuple(edge.edge_id for edge in route_edges if not _has_accessibility_evidence(edge))
    coverage = 1.0 - (len(unknown) / len(route_edges)) if route_edges else 1.0

    return CandidateRoute(
        nodes=tuple(nodes),
        distance_m=distances[end],
        evidence_coverage=coverage,
        unknown_edges=unknown,
        excluded_edges=tuple(sorted(excluded)),
    )
