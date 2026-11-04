from __future__ import annotations

import unittest

from accesstrace.routing import NoRouteError, RouteEdge, find_candidate_route


class CandidateRouteTests(unittest.TestCase):
    def test_avoids_steps_without_wheelchair_ramp(self) -> None:
        edges = (
            RouteEdge("start", "stairs", 5, {"highway": "steps"}),
            RouteEdge("stairs", "end", 5, {"highway": "footway"}),
            RouteEdge("start", "ramp", 8, {"highway": "footway", "surface": "concrete"}),
            RouteEdge("ramp", "end", 8, {"highway": "footway", "wheelchair": "yes"}),
        )

        route = find_candidate_route(edges, "start", "end")

        self.assertEqual(route.nodes, ("start", "ramp", "end"))
        self.assertEqual(route.distance_m, 16)
        self.assertIn("stairs:start", route.excluded_edges)

    def test_avoids_raised_kerb(self) -> None:
        edges = (
            RouteEdge("start", "blocked", 3, {"highway": "footway", "kerb": "raised"}),
            RouteEdge("blocked", "end", 3, {"highway": "footway"}),
            RouteEdge("start", "open", 5, {"highway": "footway", "kerb": "lowered"}),
            RouteEdge("open", "end", 5, {"highway": "footway", "surface": "asphalt"}),
        )

        route = find_candidate_route(edges, "start", "end")

        self.assertEqual(route.nodes, ("start", "open", "end"))
        self.assertIn("blocked:start", route.excluded_edges)

    def test_allows_steps_with_designated_wheelchair_ramp(self) -> None:
        edges = (
            RouteEdge(
                "start",
                "end",
                7,
                {"highway": "steps", "ramp:wheelchair": "designated"},
            ),
        )

        route = find_candidate_route(edges, "start", "end")

        self.assertEqual(route.nodes, ("start", "end"))
        self.assertEqual(route.evidence_coverage, 1.0)

    def test_active_temporary_barrier_forces_reroute(self) -> None:
        edges = (
            RouteEdge("start", "short", 3, {"highway": "footway", "wheelchair": "yes"}),
            RouteEdge("short", "end", 3, {"highway": "footway", "wheelchair": "yes"}),
            RouteEdge("start", "long", 5, {"highway": "footway", "surface": "concrete"}),
            RouteEdge("long", "end", 5, {"highway": "footway", "surface": "concrete"}),
        )

        route = find_candidate_route(edges, "start", "end", active_barriers={"short:end"})

        self.assertEqual(route.nodes, ("start", "long", "end"))
        self.assertEqual(route.distance_m, 10)

    def test_reports_unknown_evidence_without_treating_it_as_blocked(self) -> None:
        edges = (
            RouteEdge("start", "middle", 4, {"highway": "footway", "surface": "asphalt"}),
            RouteEdge("middle", "end", 6, {"highway": "footway"}),
        )

        route = find_candidate_route(edges, "start", "end")

        self.assertEqual(route.evidence_coverage, 0.5)
        self.assertEqual(route.unknown_edges, ("end:middle",))

    def test_raises_clear_error_when_no_candidate_route_exists(self) -> None:
        edges = (RouteEdge("start", "end", 5, {"highway": "steps"}),)

        with self.assertRaisesRegex(NoRouteError, "No candidate route"):
            find_candidate_route(edges, "start", "end")

    def test_rejects_non_positive_distance(self) -> None:
        with self.assertRaisesRegex(ValueError, "distance must be positive"):
            RouteEdge("start", "end", 0, {"highway": "footway"})


if __name__ == "__main__":
    unittest.main()
