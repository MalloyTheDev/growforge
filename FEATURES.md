# GrowForge — Feature Tracker

> Last updated: 2026-03-29

---

## Completed Features (Working)

### Core Infrastructure
- [x] SQLite database with 14 tables, WAL mode, foreign keys
- [x] SQL injection protection via table/column whitelisting
- [x] Auto-directory creation (data, assets, photos, backups, exports)
- [x] Welcome wizard with Beginner/Advanced mode selection
- [x] Sample data loader for first launch
- [x] Dark and light theme color schemes
- [x] Sidebar navigation with lazy tab loading (11 tabs)

### Strain Library
- [x] 50 curated strains loaded on first launch
- [x] Upsert pattern — new strains added without duplicating existing ones
- [x] Strain type normalization (old values like "Sativa-dom Hybrid" → "Hybrid")
- [x] Proper classification: Indica, Sativa, Hybrid, Indica-dominant, Sativa-dominant
- [x] Autoflower flag support
- [x] Strain data includes: THC/CBD ranges, flowering time, yield, difficulty, lineage, terpenes

### Dashboard
- [x] 8 stat cards (active plants, environments, harvested, yield, mothers, crosses, journal entries, reminders)
- [x] Active plants list with stage color badges and day counters
- [x] Strain type displayed on plant cards
- [x] Upcoming reminders panel (7-day lookahead)
- [x] Recent activity feed
- [x] Uses centralized STAGE_COLORS from config (no hardcoded colors)

### Plant Manager
- [x] Add/edit/delete plants
- [x] Full lifecycle tracking (8 stages: Germination → Harvested)
- [x] Stage advancement with confirmation
- [x] Photoperiod and autoflower support
- [x] Strain type display on plant cards (Indica/Sativa/Hybrid)
- [x] Day counter from start date
- [x] Event logging with 22 event types
- [x] Photo attachments per event
- [x] Yield tracking at harvest
- [x] Form validation (empty names, invalid dates, non-numeric inputs)
- [x] Stage color badges using centralized STAGE_COLORS
- [x] Auto-reminders created on stage change (watering, feeding, training, observations)

### Environment Manager
- [x] Add/edit environments with full settings (temp, RH, CO2, light, medium)
- [x] Delete environments with confirmation and automatic plant unlinking
- [x] Safe wattage parsing (handles decimal input without crashing)
- [x] Form validation (name required)
- [x] 13 growing medium options, 10 light type options

### Grow Journal
- [x] Structured event logging per plant
- [x] Photo timeline with thumbnails
- [x] pH, EC/PPM, temperature data per entry
- [x] Filter by plant and event type

### Calendar View
- [x] Monthly calendar with event markers
- [x] Navigate between months
- [x] Events and reminders overlaid

### Smart Reminders
- [x] Background reminder engine (threaded, configurable interval)
- [x] Popup notifications with auto-dismiss (30 seconds)
- [x] Auto-generated stage-appropriate reminders on stage advancement:
  - Seedling: watering checks, first true leaves observation
  - Vegetative: veg nutrients, watering schedule, LST/topping
  - Flowering: bloom nutrients, 12/12 light confirmation, preflower check
  - Flushing: plain water reminders, trichome checks
  - Drying: stem snap test
  - Curing: jar burping, cure quality checks
- [x] Manual reminder creation
- [x] Recurring reminder support (watering, feeding)
- [x] 7-day dashboard lookahead

### Stage Guidance Engine
- [x] Per-stage growing guides (auto/photo-aware)
- [x] Temperature, humidity, VPD, and light targets
- [x] Stage checklists and tips

### Nutrient Deficiency Wizard
- [x] Multi-symptom selector
- [x] Weighted confidence scoring
- [x] pH lockout detection
- [x] Cause identification and fix recommendations

### AI Assistant
- [x] Self-contained expert system (no internet, no API keys)
- [x] Intent classification for natural language queries
- [x] Entity extraction (plant names, strains, stages, nutrients)
- [x] Symptom decision trees with weighted confidence
- [x] Data analysis of plant logs, pH, VPD, environment
- [x] Proactive alerts for detected issues
- [x] Adaptive learning from user feedback (thumbs up/down)
- [x] Self-coding engine (writes rules to learned_rules.py, hot-reloads)
- [x] Photo description button (renamed from icon-only to "Describe")
- [x] Clear chat button

### Cloning Station
- [x] Mother plant management
- [x] Batch clone tracking with cut counts
- [x] Clone status through 5 stages
- [x] 7 rooting method options
- [x] Form validation (batch name, mother ID, cut count)

### Breeding Lab
- [x] Cross records with parent plant linking
- [x] Seed count tracking
- [x] Phenotype scoring (10 categories)
- [x] Auto-calculated average scores
- [x] Form validation (cross name, plant IDs, seed count, pheno name, flowering days)

### Tools
- [x] VPD calculator with zone chart
- [x] Nutrient mixer
- [x] Yield estimator
- [x] Training technique library

### PDF Reports
- [x] Export grow journals as formatted PDF

### Shared UI Utilities (helpers.py)
- [x] Toast notifications (success, error, warning, info)
- [x] `validate_not_empty()` — prevents empty name submissions
- [x] `validate_date()` — enforces YYYY-MM-DD format
- [x] `validate_positive_number()` — numeric input validation
- [x] `safe_int()` / `safe_float()` — crash-proof numeric parsing
- [x] `extract_id_from_option()` — safe ID extraction from dropdown strings
- [x] `show_validation_error()` — inline error labels in dialogs

---

## Recent Improvements (This Session)

### Bug Fixes
- **Strain dropdown only showing 3 strains** — Changed strain loader from "only load if empty" to upsert pattern; synced 38 missing strains into existing DB (now 50 total)
- **Inconsistent strain types** — Added normalization queries to fix old values like "Sativa-dom Hybrid", "Indica-dom", "Indica Auto"
- **Wattage crash on decimal input** — Replaced `int()` with `safe_int()` (does `int(float(value))`) in environment dialogs
- **Empty name silent fallback** — Added validation checks that show error labels instead of silently accepting "Unnamed"
- **Variable shadowing** — Renamed local `safe_float` in `_log_event_dialog` to `opt_float` to avoid conflict with imported helper

### UI/UX Improvements
- Centralized STAGE_COLORS usage across dashboard and plants tab (no more hardcoded color dicts)
- Added strain type display on plant cards (shows Indica/Sativa/Hybrid badge)
- Added delete button for environments with confirmation and plant unlinking
- Added "Clear Chat" button to AI assistant
- Renamed AI photo button from icon-only "📸" to "📸 Describe" for clarity
- Created shared helpers.py module for consistent validation and notifications

### Automation
- Auto-reminder system creates stage-appropriate reminders when advancing plant stages
- Recurring reminders for watering and feeding schedules

---

## Known Issues / To Be Fixed

- [ ] **Tests require GUI environment** — 2 of 8 integration tests fail because customtkinter can't be imported in headless environments. Need to mock or skip GUI-dependent tests.
- [ ] **Settings tab theme toggle** — Changing theme requires app restart to fully take effect
- [ ] **Calendar performance** — Large numbers of events can slow down month rendering
- [ ] **Photo storage** — Photos are stored as full-size files; no thumbnail generation for faster loading
- [ ] **Reminder popup stacking** — Multiple reminders firing at once can stack popups on top of each other

---

## Future Feature Ideas

### High Priority
- [ ] **Data backup/restore UI** — One-click database backup and restore from within the app
- [ ] **Batch operations** — Select multiple plants for bulk stage advance, watering logs, etc.
- [ ] **Search across all tabs** — Global search for plants, strains, events, notes
- [ ] **Grow timeline visualization** — Visual timeline showing a plant's full lifecycle with milestones

### Medium Priority
- [ ] **Environment monitoring integration** — Import sensor data (temp/humidity) from CSV or serial
- [ ] **Nutrient schedule templates** — Pre-built feed charts for popular nutrient lines (General Hydroponics, Fox Farm, etc.)
- [ ] **Clone-to-harvest lineage view** — Visual tree showing mother → clones → harvests
- [ ] **Comparative analytics** — Side-by-side comparison of grows (yield, timeline, inputs)
- [ ] **Custom event types** — Let users add their own event categories
- [ ] **Photo gallery view** — Browse all photos across plants with filtering

### Low Priority
- [ ] **Multi-language support** — i18n for non-English growers
- [ ] **Keyboard shortcuts** — Power user navigation (Ctrl+N new plant, Ctrl+S save, etc.)
- [ ] **Print-friendly journal** — Optimized print CSS/layout for physical logbooks
- [ ] **Strain review/rating system** — Rate strains after harvest with personal notes
- [ ] **Grow cost tracker** — Track electricity, nutrients, medium costs per grow
- [ ] **Weather integration** — For outdoor growers, pull local weather data
- [ ] **Mobile companion** — Read-only web UI for checking status from phone (local network)
