from __future__ import annotations

from io import StringIO
from pathlib import Path
import unittest

from accesstrace.osm import parse_osm


FIXTURE = Path(__file__).parent / "fixtures" / "campus.osm.xml"


class OsmParserTests(unittest.TestCase):
    def test_extracts_only_supported_pedestrian_edges(self) -> None:
        graph = parse_osm(FIXTURE)

        self.assertEqual(len(graph.edges), 3)
        self.assertEqual(
            {edge.tags["highway"] for edge in graph.edges},
            {"footway", "steps"},
        )
        self.assertTrue(all(edge.distance_m > 0 for edge in graph.edges))

    def test_combines_way_and_endpoint_accessibility_tags(self) -> None:
        graph = parse_osm(FIXTURE)
        edges = {edge.edge_id: edge for edge in graph.edges}

        self.assertEqual(edges["1:2"].tags["surface"], "concrete")
        self.assertEqual(edges["1:2"].tags["kerb"], "raised")
        self.assertEqual(edges["2:3"].tags["kerb"], "raised")
        self.assertEqual(edges["3:4"].tags["ramp:wheelchair"], "yes")

    def test_maps_named_building_to_nearest_pedestrian_node(self) -> None:
        graph = parse_osm(FIXTURE)

        self.assertEqual(len(graph.places), 1)
        self.assertEqual(graph.places[0].name, "Test Library")
        self.assertEqual(graph.places[0].nearest_node_id, "4")

    def test_rejects_way_that_references_missing_node(self) -> None:
        malformed = StringIO(
            """<osm version="0.6">
            <node id="1" lat="40" lon="-74" />
            <way id="10"><nd ref="1"/><nd ref="999"/><tag k="highway" v="footway"/></way>
            </osm>"""
        )

        with self.assertRaisesRegex(ValueError, "missing node 999"):
            parse_osm(malformed)

    def test_rejects_file_without_supported_pedestrian_network(self) -> None:
        empty_network = StringIO(
            """<osm version="0.6">
            <node id="1" lat="40" lon="-74" />
            <node id="2" lat="40" lon="-73.9" />
            <way id="10"><nd ref="1"/><nd ref="2"/><tag k="highway" v="residential"/></way>
            </osm>"""
        )

        with self.assertRaisesRegex(ValueError, "No supported pedestrian network"):
            parse_osm(empty_network)


if __name__ == "__main__":
    unittest.main()
