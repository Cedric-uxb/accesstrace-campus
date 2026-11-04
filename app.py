from __future__ import annotations

from datetime import datetime, timedelta, timezone
import os
from pathlib import Path

import streamlit as st

from accesstrace.barriers import TemporaryBarrier, active_barrier_ids
from accesstrace.osm import OsmGraph, Place, parse_osm
from accesstrace.routing import NoRouteError, find_candidate_route


DEFAULT_DATA = Path("data/raw/drew-campus.osm.xml")


@st.cache_resource(show_spinner=False)
def load_graph(path: str, modified_ns: int) -> OsmGraph:
    del modified_ns
    return parse_osm(path)


def place_label(place: Place) -> str:
    return f"{place.name} · OSM {place.osm_id}"


def default_index(places: list[Place], name: str, fallback: int) -> int:
    return next((index for index, place in enumerate(places) if place.name == name), fallback)


def route_map(graph: OsmGraph, node_ids: tuple[str, ...]) -> None:
    import pydeck as pdk

    coordinates = [[graph.coordinates[node_id][1], graph.coordinates[node_id][0]] for node_id in node_ids]
    center_lon = sum(point[0] for point in coordinates) / len(coordinates)
    center_lat = sum(point[1] for point in coordinates) / len(coordinates)
    deck = pdk.Deck(
        initial_view_state=pdk.ViewState(latitude=center_lat, longitude=center_lon, zoom=16, pitch=0),
        layers=[
            pdk.Layer(
                "PathLayer",
                data=[{"path": coordinates}],
                get_path="path",
                get_color=[29, 111, 164],
                width_min_pixels=5,
            ),
            pdk.Layer(
                "ScatterplotLayer",
                data=[{"position": coordinates[0]}, {"position": coordinates[-1]}],
                get_position="position",
                get_fill_color=[197, 73, 63],
                get_radius=5,
                radius_min_pixels=7,
            ),
        ],
    )
    st.pydeck_chart(deck, width="stretch")


def evidence_rows(route) -> list[dict[str, str]]:
    rows = []
    for index, edge in enumerate(route.edges, start=1):
        evidence = {
            key: edge.tags.get(key, "unknown")
            for key in ("wheelchair", "kerb", "surface", "incline", "smoothness", "ramp:wheelchair")
        }
        rows.append(
            {
                "segment": str(index),
                "edge_id": edge.edge_id,
                "highway": edge.tags.get("highway", "unknown"),
                **evidence,
            }
        )
    return rows


def main() -> None:
    st.set_page_config(page_title="AccessTrace Campus", layout="wide")
    st.title("AccessTrace Campus")
    st.caption("Outdoor candidate routing with visible accessibility evidence")
    st.warning(
        "Candidate route only. Open map evidence may be incomplete or outdated. "
        "Verify current conditions on site before travel."
    )

    data_path = Path(os.environ.get("ACCESSTRACE_OSM_PATH", DEFAULT_DATA))
    if not data_path.exists():
        st.error("Campus data is missing. Run `python scripts/download_osm.py` and reload the app.")
        st.stop()

    graph = load_graph(str(data_path), data_path.stat().st_mtime_ns)
    places = list(graph.places)
    if len(places) < 2:
        st.error("The selected OSM extract does not contain two named places connected to the pedestrian network.")
        st.stop()

    now = datetime.now(timezone.utc)
    if "barriers" not in st.session_state:
        st.session_state.barriers = []
    st.session_state.barriers = [barrier for barrier in st.session_state.barriers if barrier.is_active(now)]

    with st.sidebar:
        st.header("Route")
        start_index = default_index(places, "University Commons", 0)
        start = st.selectbox("Start", places, index=start_index, format_func=place_label)
        end_options = [
            place for place in places if place.nearest_node_id != start.nearest_node_id
        ]
        if not end_options:
            st.error("No destination connects to a different pedestrian-network node.")
            st.stop()
        end_index = default_index(end_options, "Hall of Sciences", 0)
        end = st.selectbox("Destination", end_options, index=end_index, format_func=place_label)

        active = active_barrier_ids(st.session_state.barriers, now)
        st.metric("Active temporary barriers", len(active))
        if active and st.button("Clear temporary barriers", width="stretch"):
            st.session_state.barriers = []
            st.rerun()

    try:
        route = find_candidate_route(
            graph.edges,
            start.nearest_node_id,
            end.nearest_node_id,
            active_barriers=active,
        )
    except NoRouteError:
        st.error("No candidate route remains after applying the current known barriers.")
        st.stop()

    metric_columns = st.columns(3)
    metric_columns[0].metric("Candidate distance", f"{route.distance_m:.0f} m")
    metric_columns[1].metric("Evidence coverage", f"{route.evidence_coverage:.0%}")
    metric_columns[2].metric("Unknown segments", len(route.unknown_edges))

    if not route.edges:
        st.info("Start and destination map to the same pedestrian-network node.")
        st.stop()

    route_map(graph, route.nodes)

    left, right = st.columns([3, 2])
    with left:
        st.subheader("Route evidence")
        st.dataframe(evidence_rows(route), hide_index=True, width="stretch")

    with right:
        st.subheader("Temporary barrier")
        selected_index = st.selectbox(
            "Route segment",
            range(len(route.edges)),
            format_func=lambda index: (
                f"Segment {index + 1} · "
                f"{route.edges[index].tags.get('highway', 'unknown')}"
            ),
        )
        selected_edge = route.edges[selected_index]
        reason = st.selectbox("Reason", ("construction", "path closure", "surface damage", "other"))
        duration = st.selectbox("Expires after", (30, 60, 120), format_func=lambda value: f"{value} minutes")
        if st.button("Add temporary barrier", type="primary", width="stretch"):
            st.session_state.barriers = [
                *st.session_state.barriers,
                TemporaryBarrier(
                    edge_id=selected_edge.edge_id,
                    created_at=now,
                    expires_at=now + timedelta(minutes=duration),
                    reason=reason,
                ),
            ]
            st.rerun()

        for barrier in st.session_state.barriers:
            st.caption(f"{barrier.edge_id} · {barrier.reason} · expires {barrier.expires_at:%H:%M UTC}")

    st.divider()
    st.caption(
        "Map data © OpenStreetMap contributors, ODbL; basemap © CARTO. "
        "Temporary reports use non-persistent application session state."
    )


if __name__ == "__main__":
    main()
