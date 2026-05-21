# GrowForge — Qt6 / C++

A C++/Qt6 (Qt Widgets) rewrite of the GrowForge desktop cannabis grow assistant,
originally a Python/customtkinter app. The UI adopts the "command center" dark
design from the `Growjs/` React prototype while preserving the full feature set
and SQLite data model of the Python app.

> From Seed to Harvest, Clone to Cross — 100% local & offline.

## Features

Twelve screens, all backed by a local SQLite database:

- **Dashboard** — stat cards, active plants, upcoming reminders, recent activity
- **Growing Hub** — Seed / Veg / Flower guidance (targets, checklists, common issues)
- **Plants** — add/edit, stage advancement, event logging, PDF report, archive
- **Environments** — tents/rooms with full settings; delete unlinks plants
- **Grow Journal** — filterable event log with readings (pH/EC/temp/RH/VPD)
- **Calendar** — monthly grid with event + reminder markers
- **Cloning** — mother plants, clone batches, rooting progress, promote-to-plant
- **Breeding Lab** — crosses with parent linking, phenotype scoring (10 categories)
- **Deficiency Wizard** — multi-symptom weighted diagnosis with pH-lockout context
- **Tools** — VPD calculator + zone chart, yield estimator, nutrient mixer, training library
- **Settings** — theme, mode, units, reminder intervals, data export

The knowledge base (50 strains, stage guides, symptom patterns, nutrient/pest data,
training techniques) is exported verbatim from the Python `knowledge_base.py` into
`resources/knowledge.json` and loaded at runtime.

## Prerequisites

- **Qt 6** (6.5+) with the `Widgets`, `Sql`, and `PrintSupport` modules
- **CMake** 3.21+
- A **C++17** compiler. On Windows, the MinGW kit bundled with Qt works well.

## Build (Windows, MinGW kit)

```sh
cmake -G Ninja -B build -S . \
  -DCMAKE_PREFIX_PATH="C:/Qt/Qt6.11.0/6.11.0/mingw_64" \
  -DCMAKE_CXX_COMPILER="C:/Qt/Qt6.11.0/Tools/mingw1310_64/bin/g++.exe" \
  -DCMAKE_BUILD_TYPE=Release
cmake --build build
```

(Adjust the Qt version/paths to your install. An MSVC kit works too — point
`CMAKE_PREFIX_PATH` at the `msvc2022_64` directory and drop the compiler override.)

## Run

The executable expects Qt's runtime DLLs on `PATH`. Either add
`<Qt>/6.x/<kit>/bin` and `<Qt>/Tools/<mingw>/bin` to `PATH`, or deploy a
self-contained bundle:

```sh
build/growforge.exe                       # if Qt bin is on PATH
# or, for a distributable folder:
windeployqt build/growforge.exe
```

On first launch the app creates `data/`, `photos/`, `exports/`, `backups/`,
the SQLite database `growforge.db` (next to the executable), loads the strain
library, and inserts sample data.

## Project layout

```
src/
  app/        Config (constants, palette) + Theme (QSS generation)
  data/       Models (Row helpers), Database (Qt SQL), KnowledgeBase (JSON)
  core/       VpdCalculator, ReminderEngine, Exporter (PDF/CSV), AiEngine
  ui/         MainWindow (sidebar+topbar+stack), Page/ScrollPage, Toast, Helpers
    widgets/  Icons, CommonWidgets (Card/Badge/MetricCard), Sparkline, VpdChart
    dialogs/  Plant/Event/Environment/CloneBatch/Breeding dialogs
    pages/    The twelve screens
resources/    style.qss, sample_data.sql, knowledge.json (Qt resource)
```

## Notes

- The original Python app's "AI Assistant" is intentionally **not** ported.
- Charts (sparklines, VPD zone grid) are drawn with `QPainter` — no extra deps.
- A few `GROWFORGE_*` environment variables (`SHOT`, `NAV`, `SIZE`) drive
  headless screenshots for development and are inert unless set.
```
