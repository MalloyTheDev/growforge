# GrowForge — Qt 6 / C++

A C++/Qt 6 (Qt Widgets) implementation of the GrowForge desktop grow assistant
— originally a Python/customtkinter app. The UI adopts the dark "command-center"
design from the prototype in [`../design/`](../design) while preserving the full
feature set and SQLite data model.

> From Seed to Harvest, Clone to Cross — 100% local & offline.

This document covers building, running, and the project structure. For a feature
overview and screenshots, see the [repository README](../README.md).

## Prerequisites

| Tool | Version | Notes |
|---|---|---|
| **Qt** | 6.5+ (developed on 6.11) | Modules: `Widgets`, `Sql`, `PrintSupport` |
| **CMake** | 3.21+ | |
| **Compiler** | any C++17 | MinGW (bundled with Qt) or MSVC on Windows; GCC/Clang on Linux |
| **Ninja** | optional | Recommended generator |

## Build

### Windows — MinGW (the kit bundled with Qt)

The Qt MinGW build is ABI-specific, so use the matching bundled compiler:

```sh
cmake -G Ninja -B build -S . \
  -DCMAKE_PREFIX_PATH="C:/Qt/Qt6.11.0/6.11.0/mingw_64" \
  -DCMAKE_CXX_COMPILER="C:/Qt/Qt6.11.0/Tools/mingw1310_64/bin/g++.exe" \
  -DCMAKE_BUILD_TYPE=Release
cmake --build build
```

### Windows — MSVC

```sh
cmake -G Ninja -B build -S . ^
  -DCMAKE_PREFIX_PATH="C:/Qt/Qt6.11.0/6.11.0/msvc2022_64" ^
  -DCMAKE_BUILD_TYPE=Release
cmake --build build
```

### Linux

```sh
cmake -G Ninja -B build -S . -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_PREFIX_PATH="$HOME/Qt/6.11.0/gcc_64"   # or distro Qt6 (omit if on PATH)
cmake --build build
```

Adjust the Qt version and paths to match your installation.

## Run

The executable needs Qt's runtime libraries available. Either add the Qt `bin`
directory (and, for MinGW, the compiler `bin`) to your `PATH`, or deploy a
self-contained folder:

```sh
# If the Qt bin directory is on PATH:
build/growforge.exe

# Otherwise, copy the required Qt DLLs/plugins next to the executable (Windows):
windeployqt --release --compiler-runtime build/growforge.exe
```

> **Tip (Windows):** if double-clicking the `.exe` reports a missing entry point
> such as `qt_version_tag_6_xx`, an *older* Qt is being picked up from your `PATH`.
> Running `windeployqt` places the correct Qt libraries beside the executable,
> which take precedence and resolve the mismatch.

On first launch the app creates `data/`, `photos/`, `exports/`, and `backups/`
folders, creates the SQLite database `growforge.db` next to the executable, loads
the strain library, and inserts sample data so the screens aren't empty.

## Project layout

```
src/
  app/        Config (constants, color palette) + Theme (QSS generation)
  data/       Models (Row helpers), Database (Qt SQL), KnowledgeBase (JSON loader)
  core/       VpdCalculator, ReminderEngine, Exporter (PDF/CSV)
  ui/         MainWindow (sidebar + topbar + stacked pages), Page/ScrollPage,
              Toast, Helpers (validation)
    widgets/  Icons, CommonWidgets (Card/Badge/MetricCard), Sparkline, VpdChart
    dialogs/  Plant / Event / Environment / CloneBatch / Breeding dialogs
    pages/    The eleven screens
resources/    style.qss, sample_data.sql, knowledge.json  (compiled in via Qt resources)
docs/         Screenshots
```

## Implementation notes

- **Theme** — the whole UI is a single QSS stylesheet generated at runtime from a
  typed `Config::Palette`, so the dark/light themes share one source of truth.
- **Database** — `QtSql` over SQLite with WAL mode and foreign keys. Generic CRUD is
  guarded by table/column whitelisting and numeric field-range validation; phenotype
  overall scores are auto-averaged on insert.
- **Knowledge base** — the data in the original Python `knowledge_base.py` (50 strains,
  stage guides, symptom patterns, nutrient/pest data, training techniques) is exported
  verbatim to `resources/knowledge.json` and parsed at runtime, so it stays faithful to
  the source with no hand-transcription.
- **Charts** — sparklines and the VPD zone chart are custom `QPainter` widgets; there is
  no QtCharts dependency.
- **Reminders** — a `QTimer` on the GUI thread polls for due reminders (safe with Qt SQL)
  and creates stage-appropriate reminders when a plant advances.
- **Dev hooks** — `GROWFORGE_SHOT=<path>` renders the window to a PNG and exits;
  `GROWFORGE_NAV=<page>` and `GROWFORGE_SIZE=WxH` set the initial page and size. These
  are inert unless the environment variables are set.

## License

MIT — see [LICENSE](../LICENSE).
