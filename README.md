# GrowForge

**From Seed to Harvest, Clone to Cross — the local-first desktop grow assistant.**

GrowForge is a 100% local, offline desktop app for tracking a cannabis grow end to
end: plants and their full lifecycle, environments, a structured grow journal,
cloning, breeding and phenotype hunting, a deficiency diagnosis wizard, and a set
of grow calculators. All data lives in a local SQLite database — nothing leaves
your machine.

Built in **C++ with Qt 6 (Qt Widgets)**, with a dense, dark "command center" UI.

![Dashboard](growforge-qt/docs/dashboard.png)

## Screens

| | |
|---|---|
| ![Plants](growforge-qt/docs/plants.png) | ![Growing Hub](growforge-qt/docs/growing.png) |
| ![Grow Journal](growforge-qt/docs/journal.png) | ![Calendar](growforge-qt/docs/calendar.png) |
| ![Tools — VPD](growforge-qt/docs/tools.png) | ![Cloning](growforge-qt/docs/cloning.png) |
| ![Breeding Lab](growforge-qt/docs/breeding.png) | ![Deficiency Wizard](growforge-qt/docs/deficiency.png) |

## Features

- **Dashboard** — at-a-glance stat cards, active plants with stage badges and day
  counters, upcoming reminders, and a recent-activity feed.
- **Growing Hub** — Seed / Veg / Flower phases with stage-specific targets
  (temp, RH, VPD, PPFD, light schedule), checklists, and common-issue fixes.
- **Plants** — add/edit, advance through 8 lifecycle stages (auto-logging a stage
  change and creating stage-appropriate reminders), log events, track yield, and
  export a per-plant PDF grow report.
- **Environments** — tents, cabinets, and rooms with light, schedule, medium, and
  size; deleting one safely unlinks its plants.
- **Grow Journal** — every logged event, filterable by plant and type, with
  pH / EC / PPM / temp / RH / VPD / water readings.
- **Calendar** — month grid with event and reminder markers.
- **Cloning Station** — mother plants, clone batches, per-cutting rooting progress,
  and one-click promotion of a rooted clone into a tracked plant.
- **Breeding Lab** — crosses with parent linking, seed counts and generations, and
  phenotype scoring across 10 categories with an auto-calculated overall score.
- **Deficiency Wizard** — pick the symptoms you see and get a weighted, ranked
  diagnosis with fixes and pH-lockout context for your medium.
- **Tools** — a VPD calculator with a live temperature/humidity zone chart, a yield
  estimator, a nutrient mixer, and a training-technique library.
- **Settings** — theme, experience mode, units, reminder intervals, and CSV export.

A built-in knowledge base ships 50 strains plus stage guides, symptom patterns,
nutrient and pest data, and training techniques.

## Tech stack

- **C++17** / **Qt 6** (Widgets, SQL, PrintSupport)
- **SQLite** for all storage (WAL mode, foreign keys, 11 tables)
- **CMake** + **Ninja** build
- Charts (sparklines, VPD zone grid) drawn directly with `QPainter` — no extra deps
- PDF reports via `QTextDocument` → `QPrinter`

## Build & run

The app lives in [`growforge-qt/`](growforge-qt/). With a Qt 6 install and a C++17
compiler:

```sh
cd growforge-qt
cmake -G Ninja -B build -S . -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_PREFIX_PATH="<path-to-Qt>/6.x/<kit>"
cmake --build build
```

On Windows with the MinGW kit bundled with Qt, also pass
`-DCMAKE_CXX_COMPILER="<path-to-Qt>/Tools/<mingw>/bin/g++.exe"`. See
[`growforge-qt/README.md`](growforge-qt/README.md) for the exact commands and for
producing a standalone bundle with `windeployqt`.

On first launch the app creates its data folders and SQLite database next to the
executable, loads the strain library, and seeds sample data so you can explore.

## Repository layout

```
growforge-qt/     The Qt 6 / C++ application (source, resources, build docs)
  src/            app · data · core · ui (widgets, dialogs, pages)
  resources/      QSS theme, sample data, embedded knowledge base
  docs/           Screenshots
design/           The original UI design prototype the app's look is based on
```

## License

See [LICENSE](LICENSE).
