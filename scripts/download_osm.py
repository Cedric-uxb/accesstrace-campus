from __future__ import annotations

import argparse
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET


BBOX = (-74.4335348, 40.7557486, -74.4199348, 40.7654240)
DEFAULT_DESTINATION = Path("data/raw/drew-campus.osm.xml")


def download(destination: Path) -> None:
    query = urlencode({"bbox": ",".join(map(str, BBOX))})
    request = Request(
        f"https://api.openstreetmap.org/api/0.6/map?{query}",
        headers={"User-Agent": "AccessTrace-Campus/0.1"},
    )
    with urlopen(request, timeout=60) as response:
        payload = response.read()

    if ET.fromstring(payload).tag != "osm":
        raise ValueError("OpenStreetMap response is not an OSM document")

    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(destination.suffix + ".tmp")
    temporary.write_bytes(payload)
    temporary.replace(destination)


def main() -> None:
    parser = argparse.ArgumentParser(description="Download the bounded Drew University OSM extract")
    parser.add_argument("--destination", type=Path, default=DEFAULT_DESTINATION)
    args = parser.parse_args()
    download(args.destination)
    print(f"Downloaded OpenStreetMap extract to {args.destination}")


if __name__ == "__main__":
    main()
