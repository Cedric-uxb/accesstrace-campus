# AccessTrace Campus — Devpost Draft

This file is a Devpost submission draft. The public repository and demo assets exist, but the project has not been registered or submitted on Devpost.

## Submission status

- Pathway: Hackathon Pathway
- Public repository: verified anonymously on November 11, 2026
- Devpost account state: not logged in in the current browser session
- Hackathon registration: not yet completed
- Internal hard deadline: November 15, 2026 at 7:00 PM CST (8:00 PM EST)
- Devpost overview deadline: November 15, 2026 at 9:30 PM CST (10:30 PM EST)
- Reason for the earlier cutoff: the official rules body and overview disagree, so the earlier published time is used.

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

Python, Streamlit, PyDeck, OpenStreetMap XML, unittest, coverage.py, Orpheus TTS, FFmpeg

## AI and third-party resources

- Orpheus TTS generated the English demo narration locally using the `tara` voice.
- FFmpeg combined the narration and project screenshots into the demo video.
- Streamlit and PyDeck power the interface and map visualization.
- OpenStreetMap supplies the campus path data; CARTO supplies map tiles in the prototype.
- AI-assisted development was used for planning, code review, debugging, documentation, and test preparation. The participant reviewed the implementation and can explain the routing rules and limitations.

## Links

- Public repository: <https://github.com/Cedric-uxb/accesstrace-campus>
- Reproducible local demo: <https://github.com/Cedric-uxb/accesstrace-campus#run-locally>
- Demo video: <https://raw.githubusercontent.com/Cedric-uxb/accesstrace-campus/main/demo/AccessTrace-Campus-Demo.mp4>
- Desktop screenshot: <https://raw.githubusercontent.com/Cedric-uxb/accesstrace-campus/main/docs/screenshots/access-trace-desktop.jpg>
- Reroute screenshot: <https://raw.githubusercontent.com/Cedric-uxb/accesstrace-campus/main/docs/screenshots/access-trace-reroute.jpg>
- Mobile screenshot: <https://raw.githubusercontent.com/Cedric-uxb/accesstrace-campus/main/docs/screenshots/access-trace-mobile.jpg>

## Final checklist

- [x] Public repository URL opens without login.
- [x] Live demo or reproducible local instructions are available.
- [x] Demo video is public or unlisted and no longer than 3 minutes.
- [x] Repository contains no raw OSM extract, token, private email, local path, or account information.
- [x] README, OSM/CARTO attribution, and third-party notices are visible.
- [x] Devpost deadline was checked on November 11, 2026; use the earlier 7:00 PM CST time if official pages still disagree.
- [ ] Log in to Devpost and register for STEMergent Hacks 2026.
- [ ] Create the AccessTrace Campus Hackathon Pathway submission and enter the prepared fields above.
- [ ] Submission success page or receipt is saved before changing status to `submitted`.
