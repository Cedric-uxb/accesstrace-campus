# AccessTrace Campus — Devpost Draft

This file is a draft only. It is not evidence that a Devpost submission or public repository exists.

## Project name

AccessTrace Campus

## Tagline

Evidence-first outdoor campus routing that shows what the map knows, what remains unknown, and how temporary barriers change the route.

## Inspiration

People with reduced mobility need more than the shortest line between two buildings. Ordinary maps often hide whether a path includes steps, raised kerbs, rough surfaces, or simply missing accessibility data. AccessTrace Campus was inspired by the need to make that uncertainty visible before a person decides how to travel.

## What it does

AccessTrace Campus calculates an outdoor candidate route between named campus places using a bounded OpenStreetMap extract. It excludes explicit blockers such as `wheelchair=no`, `access/foot=no/private`, raised kerbs, and steps without a designated wheelchair ramp. The interface reports route distance, evidence coverage, unknown segments, and a segment-level evidence ledger.

A user can add a temporary barrier with a reason and expiry time. The app then recalculates the route or clearly reports that no candidate route remains. Temporary reports stay in non-persistent application session state and are not written back to OpenStreetMap.

The prototype does not certify safety, ADA compliance, current conditions, or a verified accessible entrance. It asks users to verify conditions on site.

## How we built it

- Python standard-library XML parsing for a fixed Drew University OpenStreetMap extract.
- A deterministic Dijkstra shortest-path implementation.
- Explicit route rules for wheelchair, access, foot, kerb, steps, and wheelchair-ramp tags.
- Streamlit and PyDeck for the single-screen route, evidence, and barrier workflow.
- Expiring, session-only temporary barriers.
- Test-first development with unit, parser, cache-refresh, and Streamlit flow tests.

Current verification: 20 tests pass with 93% branch coverage. A clean temporary environment reproduced installation, OSM download, the full test suite, and an HTTP 200 Streamlit startup.

## Challenges

Open map data is incomplete and can be outdated. The main design challenge was avoiding a false sense of certainty. Missing accessibility tags therefore remain `unknown`, and evidence coverage is shown separately from route distance. Another challenge was connecting named buildings to the outdoor network without claiming that the nearest mapped node is a verified accessible entrance.

## Accomplishments

- A reproducible real-campus route from University Commons to Hall of Sciences.
- A segment-level evidence ledger instead of a hidden accessibility score.
- Deterministic exclusion of explicit barriers and restricted paths.
- A temporary-barrier demo that changes the route from about 636 meters to 673 meters.
- Clear failure behavior when the mapped network has no alternative route.
- Desktop and 390×844 visual checks with a nonblank map and no observed overlap.

## What we learned

Accessibility routing is as much a data-quality problem as a pathfinding problem. A short route with weak evidence should not be presented with the same confidence as a field-verified route. We also learned that campus buildings can map to the same network node and that updated OSM files need cache invalidation, both of which are now covered by the implementation and tests.

## What's next

1. Map and field-verify accessible building entrances with a campus accessibility team.
2. Add verified surface, slope, kerb, and temporary construction observations.
3. Test route usefulness with people who use mobility devices.
4. Define moderation and retention rules before accepting persistent public reports.

## Technologies

Python, Streamlit, PyDeck, OpenStreetMap XML, unittest, coverage.py

## Links to add before submission

- Public repository: `TBD`
- Live demo: `TBD`
- Demo video: `TBD`

## Final checklist

- [ ] Public repository URL opens without login.
- [ ] Live demo or reproducible local instructions are available.
- [ ] Demo video is public or unlisted and no longer than 3 minutes.
- [ ] Repository contains no raw OSM extract, token, private email, local path, or account information.
- [ ] README, OSM/CARTO attribution, and third-party notices are visible.
- [ ] Devpost deadline is rechecked immediately before submission; use the earlier published time if official pages still disagree.
- [ ] Submission success page or receipt is saved before changing status to `submitted`.
