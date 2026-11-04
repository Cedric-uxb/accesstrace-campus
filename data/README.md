# Data

The prototype downloads a bounded OpenStreetMap XML extract for Drew University from the official OpenStreetMap API.

Run:

```bash
python scripts/download_osm.py
```

The raw extract is written to `data/raw/drew-campus.osm.xml` and is intentionally ignored by Git. OpenStreetMap data is available under the Open Data Commons Open Database License (ODbL); attribution is required: <https://www.openstreetmap.org/copyright>.

Snapshot boundary:

```text
west=-74.4335348
south=40.7557486
east=-74.4199348
north=40.7654240
```
