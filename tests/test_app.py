from __future__ import annotations

import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from app import load_graph
from streamlit.testing.v1 import AppTest


ROOT = Path(__file__).parents[1]
APP_PATH = ROOT / "app.py"
FIXTURE = Path(__file__).parent / "fixtures" / "campus.osm.xml"


class AppSmokeTests(unittest.TestCase):
    def test_candidate_route_and_temporary_barrier_flow(self) -> None:
        with patch.dict(os.environ, {"ACCESSTRACE_OSM_PATH": str(FIXTURE)}):
            app = AppTest.from_file(APP_PATH).run(timeout=30)

            self.assertFalse(app.exception)
            self.assertEqual(app.title[0].value, "AccessTrace Campus")
            self.assertTrue(
                {"Start", "Destination", "Route segment", "Reason", "Expires after"}.issubset(
                    {element.label for element in app.selectbox}
                )
            )
            self.assertTrue(
                {"Route evidence", "Temporary barrier"}.issubset(
                    {element.value for element in app.subheader}
                )
            )
            self.assertIn("Candidate route only", app.warning[0].value)
            destination = next(element for element in app.selectbox if element.label == "Destination")
            self.assertEqual(destination.options, ["Test Library · OSM 200"])

            add_barrier = next(button for button in app.button if button.label == "Add temporary barrier")
            add_barrier.click()
            app.run(timeout=30)

            self.assertFalse(app.exception)
            active_barriers = next(
                metric for metric in app.metric if metric.label == "Active temporary barriers"
            )
            self.assertEqual(active_barriers.value, "1")
            self.assertIn("No candidate route remains", app.error[0].value)

    def test_graph_cache_refreshes_when_fingerprint_changes(self) -> None:
        with TemporaryDirectory() as directory:
            path = Path(directory) / "campus.osm.xml"
            source = FIXTURE.read_text(encoding="utf-8")
            path.write_text(source, encoding="utf-8")
            first = load_graph(str(path), 1)

            path.write_text(source.replace("Test Hall", "Renamed Hall"), encoding="utf-8")
            second = load_graph(str(path), 2)

        self.assertIn("Test Hall", {place.name for place in first.places})
        self.assertIn("Renamed Hall", {place.name for place in second.places})


if __name__ == "__main__":
    unittest.main()
