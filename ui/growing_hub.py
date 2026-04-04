# FILE: growforge/ui/growing_hub.py
"""
GrowForge — Growing Hub tab.
Displays plants grouped by growth stage (Seed, Veg, Flower) with
research-backed care panels for each stage.
"""

import customtkinter as ctk
from datetime import datetime, date
from database import get_active_plants
from config import STAGE_COLORS, STAGES


class GrowingHubTab:
    """Main Growing tab with sub-tabs for Seed, Veg, and Flower stages."""

    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.colors = app.colors
        self._build()

    # ─── Top-level build ────────────────────────────────────────────────────

    def _build(self):
        outer = ctk.CTkFrame(self.parent, fg_color="transparent")
        outer.pack(fill="both", expand=True)

        # Header
        header = ctk.CTkFrame(outer, fg_color="transparent")
        header.pack(fill="x", padx=25, pady=(20, 4))

        ctk.CTkLabel(
            header,
            text="🌱 Growing Hub",
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color=self.colors["fg_primary"],
        ).pack(anchor="w")

        ctk.CTkLabel(
            header,
            text="Manage your plants by growth stage",
            font=ctk.CTkFont(size=13),
            text_color=self.colors["fg_muted"],
        ).pack(anchor="w")

        # Tab view
        tabview = ctk.CTkTabview(
            outer,
            fg_color=self.colors["bg_secondary"],
            segmented_button_fg_color=self.colors["bg_tertiary"],
            segmented_button_selected_color=self.colors["accent_dark"],
            segmented_button_selected_hover_color=self.colors["accent"],
            segmented_button_unselected_color=self.colors["bg_tertiary"],
            segmented_button_unselected_hover_color=self.colors["highlight"],
            text_color=self.colors["fg_secondary"],
            text_color_disabled=self.colors["fg_muted"],
        )
        tabview.pack(fill="both", expand=True, padx=15, pady=(8, 15))

        tabview.add("🌱 Seed & Seedling")
        tabview.add("🌿 Vegetative")
        tabview.add("🌸 Flowering")

        self._build_seed_tab(tabview.tab("🌱 Seed & Seedling"))
        self._build_veg_tab(tabview.tab("🌿 Vegetative"))
        self._build_flower_tab(tabview.tab("🌸 Flowering"))

    # ─── Helper: days since a date string ───────────────────────────────────

    @staticmethod
    def _days_since(date_str: str) -> int:
        """Return the number of whole days since a datetime string."""
        if not date_str:
            return 0
        try:
            dt = datetime.fromisoformat(date_str.split(".")[0])
            return (datetime.now() - dt).days
        except (ValueError, TypeError):
            return 0

    # ─── Helper: section card ───────────────────────────────────────────────

    def _make_info_card(self, parent, title: str, rows: list[tuple[str, str]]) -> ctk.CTkFrame:
        """
        Build a labelled info card and return it (not packed — caller handles layout).

        rows: list of (label, value) tuples. Pass None as label for a plain line.
        """
        card = ctk.CTkFrame(
            parent,
            fg_color=self.colors["bg_card"],
            corner_radius=10,
        )

        ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=self.colors["accent"],
        ).pack(anchor="w", padx=12, pady=(10, 4))

        sep = ctk.CTkFrame(card, height=1, fg_color=self.colors["border"])
        sep.pack(fill="x", padx=12, pady=(0, 6))

        for label, value in rows:
            row_frame = ctk.CTkFrame(card, fg_color="transparent")
            row_frame.pack(fill="x", padx=12, pady=1)

            if label:
                ctk.CTkLabel(
                    row_frame,
                    text=f"{label}:",
                    font=ctk.CTkFont(size=11, weight="bold"),
                    text_color=self.colors["fg_secondary"],
                    width=0,
                ).pack(side="left", anchor="nw", padx=(0, 6))

            ctk.CTkLabel(
                row_frame,
                text=value,
                font=ctk.CTkFont(size=11),
                text_color=self.colors["fg_secondary"],
                wraplength=320,
                justify="left",
            ).pack(side="left", anchor="nw", fill="x", expand=True)

        # bottom padding
        ctk.CTkFrame(card, height=8, fg_color="transparent").pack()
        return card

    # ─── Helper: plant card ─────────────────────────────────────────────────

    def _make_plant_card(
        self,
        parent,
        plant: dict,
        days_label: str = "days since sprout",
        extra_lines: list[str] | None = None,
    ) -> ctk.CTkFrame:
        """Build a single plant summary card."""
        stage = plant.get("stage", "")
        badge_color = STAGE_COLORS.get(stage, self.colors["accent_dark"])

        card = ctk.CTkFrame(
            parent,
            fg_color=self.colors["bg_card"],
            corner_radius=12,
        )

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=14, pady=10)

        # Top row: name + stage badge
        top = ctk.CTkFrame(inner, fg_color="transparent")
        top.pack(fill="x")

        ctk.CTkLabel(
            top,
            text=plant.get("name", "Unknown"),
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.colors["fg_primary"],
        ).pack(side="left")

        ctk.CTkLabel(
            top,
            text=f"  {stage}  ",
            font=ctk.CTkFont(size=10, weight="bold"),
            fg_color=badge_color,
            text_color="#ffffff",
            corner_radius=6,
        ).pack(side="right")

        # Strain
        strain = plant.get("strain_name") or plant.get("strain") or ""
        if strain:
            ctk.CTkLabel(
                inner,
                text=strain,
                font=ctk.CTkFont(size=11),
                text_color=self.colors["fg_muted"],
            ).pack(anchor="w", pady=(2, 0))

        # Days counter
        days = self._days_since(plant.get("created_at", ""))
        ctk.CTkLabel(
            inner,
            text=f"{days} {days_label}",
            font=ctk.CTkFont(size=11),
            text_color=self.colors["fg_secondary"],
        ).pack(anchor="w", pady=(2, 0))

        # Extra lines (e.g., week number, reminders)
        for line in (extra_lines or []):
            ctk.CTkLabel(
                inner,
                text=line,
                font=ctk.CTkFont(size=11),
                text_color=self.colors["fg_secondary"],
                wraplength=260,
                justify="left",
            ).pack(anchor="w", pady=(1, 0))

        return card

    # ─── Helper: empty state label ──────────────────────────────────────────

    def _empty_state(self, parent, message: str):
        ctk.CTkLabel(
            parent,
            text=message,
            font=ctk.CTkFont(size=12),
            text_color=self.colors["fg_muted"],
            wraplength=280,
            justify="center",
        ).pack(expand=True, pady=40)

    # ════════════════════════════════════════════════════════════════════════
    # SEED & SEEDLING TAB
    # ════════════════════════════════════════════════════════════════════════

    def _build_seed_tab(self, parent):
        parent.grid_columnconfigure(0, weight=3)
        parent.grid_columnconfigure(1, weight=2)
        parent.grid_rowconfigure(0, weight=1)

        # ── Left: plant list ──────────────────────────────────────────────
        left = ctk.CTkScrollableFrame(
            parent,
            fg_color="transparent",
            scrollbar_button_color=self.colors["bg_tertiary"],
        )
        left.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)

        ctk.CTkLabel(
            left,
            text="Plants at Seed / Seedling Stage",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.colors["fg_primary"],
        ).pack(anchor="w", padx=5, pady=(4, 8))

        all_plants = get_active_plants()
        seed_plants = [
            p for p in all_plants
            if p.get("stage") in ("Germination", "Seedling")
        ]

        if seed_plants:
            for plant in seed_plants:
                card = self._make_plant_card(
                    left, plant, days_label="days since sprout"
                )
                card.pack(fill="x", padx=5, pady=4)
        else:
            self._empty_state(
                left,
                "No plants in seed/seedling stage.\nAdd a plant in the Plants tab.",
            )

        # ── Right: care panel ─────────────────────────────────────────────
        right = ctk.CTkScrollableFrame(
            parent,
            fg_color="transparent",
            scrollbar_button_color=self.colors["bg_tertiary"],
        )
        right.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)

        ctk.CTkLabel(
            right,
            text="Seed & Seedling Care Guide",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.colors["fg_primary"],
        ).pack(anchor="w", padx=5, pady=(4, 8))

        # Card 1 – Environment
        env_card = self._make_info_card(
            right,
            "🌡️ Environment",
            [
                ("Germination temp", "70–85°F (21–29°C)"),
                ("Germination RH", "70–90%"),
                ("Germination light", "Darkness or 18–24 h low-intensity light"),
                ("Seedling temp", "72–80°F (22–27°C)"),
                ("Seedling RH", "65–80%"),
                ("Seedling light", "18–24 h at 200–400 µmol/m²/s PPFD"),
            ],
        )
        env_card.pack(fill="x", padx=5, pady=4)

        # Card 2 – Watering & pH
        water_card = self._make_info_card(
            right,
            "💧 Watering & pH",
            [
                ("Frequency", "Water sparingly — only when the medium surface is barely dry"),
                ("pH (soil/coco)", "6.0–7.0"),
                ("pH (hydro/rockwool)", "5.5–6.5"),
                ("Nutrients", "Plain pH'd water for first 1–2 weeks — no nutrients"),
                ("Why no nutrients", "Seedlings draw on stored nutrients in the cotyledons"),
            ],
        )
        water_card.pack(fill="x", padx=5, pady=4)

        # Card 3 – Timeline
        timeline_card = self._make_info_card(
            right,
            "⏱️ Timeline",
            [
                ("Germination", "24–72 hours (seed cracking to visible taproot)"),
                ("Seedling stage", "2–3 weeks until 3–4 sets of true leaves"),
                ("Ready for veg", "4–6 alternate leaf sets, healthy upright stem"),
            ],
        )
        timeline_card.pack(fill="x", padx=5, pady=4)

        # Card 4 – Common Issues
        issues_card = self._make_info_card(
            right,
            "⚠️ Common Issues",
            [
                ("Damping off", "Reduce humidity, improve airflow around the stem"),
                ("Stretching", "Light too far away — increase intensity or lower fixture"),
                ("Yellowing cotyledons", "Normal after ~2 weeks; true leaves should stay green"),
                ("Overwatering", "Most common beginner mistake — less is more at this stage"),
            ],
        )
        issues_card.pack(fill="x", padx=5, pady=4)

    # ════════════════════════════════════════════════════════════════════════
    # VEGETATIVE TAB
    # ════════════════════════════════════════════════════════════════════════

    def _build_veg_tab(self, parent):
        parent.grid_columnconfigure(0, weight=3)
        parent.grid_columnconfigure(1, weight=2)
        parent.grid_rowconfigure(0, weight=1)

        # ── Left: plant list ──────────────────────────────────────────────
        left = ctk.CTkScrollableFrame(
            parent,
            fg_color="transparent",
            scrollbar_button_color=self.colors["bg_tertiary"],
        )
        left.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)

        ctk.CTkLabel(
            left,
            text="Plants in Vegetative Stage",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.colors["fg_primary"],
        ).pack(anchor="w", padx=5, pady=(4, 8))

        all_plants = get_active_plants()
        veg_plants = [p for p in all_plants if p.get("stage") == "Vegetative"]

        if veg_plants:
            for plant in veg_plants:
                # Prefer veg_date for days-in-veg; fall back to created_at
                veg_start = plant.get("veg_date") or plant.get("created_at", "")
                days = self._days_since(veg_start)
                training = plant.get("training_method") or plant.get("notes", "")
                extra: list[str] = []
                if training:
                    # Show the first 60 chars of training notes
                    snippet = training[:60].strip()
                    if len(training) > 60:
                        snippet += "…"
                    extra.append(f"Training: {snippet}")
                card = self._make_plant_card(
                    left, plant,
                    days_label="days in veg",
                    extra_lines=extra,
                )
                card.pack(fill="x", padx=5, pady=4)
        else:
            self._empty_state(
                left,
                "No plants in vegetative stage.\nAdd a plant or update a plant's stage in the Plants tab.",
            )

        # ── Right: care panel ─────────────────────────────────────────────
        right = ctk.CTkScrollableFrame(
            parent,
            fg_color="transparent",
            scrollbar_button_color=self.colors["bg_tertiary"],
        )
        right.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)

        ctk.CTkLabel(
            right,
            text="Vegetative Stage Care Guide",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.colors["fg_primary"],
        ).pack(anchor="w", padx=5, pady=(4, 8))

        # Card 1 – Optimal Environment
        env_card = self._make_info_card(
            right,
            "🌡️ Optimal Environment",
            [
                ("Day temp", "70–85°F (21–29°C)"),
                ("Night temp", "64–75°F (18–24°C) — 10°F drop is ideal"),
                ("Humidity", "40–70% RH (lower gradually as canopy fills)"),
                ("VPD target", "0.8–1.2 kPa"),
                ("CO₂ (ambient)", "400–700 ppm"),
                ("CO₂ (enriched)", "1000–1500 ppm"),
            ],
        )
        env_card.pack(fill="x", padx=5, pady=4)

        # Card 2 – Lighting
        light_card = self._make_info_card(
            right,
            "💡 Lighting",
            [
                ("Schedule", "18/6 (photoperiod) or 18–24 h (autoflower)"),
                ("PPFD (beginner)", "400–600 µmol/m²/s"),
                ("PPFD (advanced)", "Up to 800 µmol/m²/s with CO₂ supplementation"),
                ("DLI target", "25–35 mol/m²/d"),
            ],
        )
        light_card.pack(fill="x", padx=5, pady=4)

        # Card 3 – Nutrients
        nutes_card = self._make_info_card(
            right,
            "🌿 Nutrients",
            [
                ("N-P-K ratio", "3-1-2 — heavy Nitrogen, moderate P and K"),
                ("EC range", "1.0–2.0 mS/cm"),
                ("pH (soil)", "6.0–7.0"),
                ("pH (hydro/coco)", "5.5–6.5"),
                ("Cal-Mag", "Calcium & Magnesium especially important under LED"),
            ],
        )
        nutes_card.pack(fill="x", padx=5, pady=4)

        # Card 4 – Training Window
        training_card = self._make_info_card(
            right,
            "✂️ Training Window",
            [
                ("LST", "Start at 4–6 nodes — bend, don't break"),
                ("Topping", "Node 4–6, creates 2 main colas"),
                ("FIM", "Node 4–6, creates 4+ colas with less stress than topping"),
                ("SCROG", "Fill net to ~50% before flipping to flower"),
                ("Deadline", "Stop major training 2 weeks before the flip"),
            ],
        )
        training_card.pack(fill="x", padx=5, pady=4)

    # ════════════════════════════════════════════════════════════════════════
    # FLOWERING TAB
    # ════════════════════════════════════════════════════════════════════════

    def _build_flower_tab(self, parent):
        parent.grid_columnconfigure(0, weight=3)
        parent.grid_columnconfigure(1, weight=2)
        parent.grid_rowconfigure(0, weight=1)

        # ── Left: plant list ──────────────────────────────────────────────
        left = ctk.CTkScrollableFrame(
            parent,
            fg_color="transparent",
            scrollbar_button_color=self.colors["bg_tertiary"],
        )
        left.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)

        ctk.CTkLabel(
            left,
            text="Plants in Flowering / Flushing",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.colors["fg_primary"],
        ).pack(anchor="w", padx=5, pady=(4, 8))

        all_plants = get_active_plants()
        flower_plants = [
            p for p in all_plants
            if p.get("stage") in ("Flowering", "Flushing")
        ]

        if flower_plants:
            for plant in flower_plants:
                # Prefer flower_date (flip date) for days-in-flower; fall back to created_at
                flower_start = plant.get("flower_date") or plant.get("created_at", "")
                days = self._days_since(flower_start)
                week_num = max(1, days // 7)
                extra: list[str] = [f"Week {week_num} of flower (day {days})"]

                if week_num >= 6:
                    extra.append("🔬 Trichome check recommended — approaching harvest window")

                # Harvest window indicator based on stage
                if plant.get("stage") == "Flushing":
                    extra.append("🚿 Currently flushing — harvest window is near")

                card = self._make_plant_card(
                    left, plant,
                    days_label="days in flower",
                    extra_lines=extra,
                )
                card.pack(fill="x", padx=5, pady=4)
        else:
            self._empty_state(
                left,
                "No plants in flowering or flushing stage.\nUpdate a plant's stage in the Plants tab.",
            )

        # ── Right: care panel ─────────────────────────────────────────────
        right = ctk.CTkScrollableFrame(
            parent,
            fg_color="transparent",
            scrollbar_button_color=self.colors["bg_tertiary"],
        )
        right.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)

        ctk.CTkLabel(
            right,
            text="Flowering Stage Care Guide",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.colors["fg_primary"],
        ).pack(anchor="w", padx=5, pady=(4, 8))

        # Card 1 – Optimal Environment
        env_card = self._make_info_card(
            right,
            "🌡️ Optimal Environment",
            [
                ("Day temp", "65–80°F (18–26°C) — cooler than veg"),
                ("Night temp", "60–70°F (15–21°C) — 10–15°F differential for colour"),
                ("Early RH (wk 1–4)", "40–50%"),
                ("Late RH (wk 5+)", "30–40% — critical to prevent mould"),
                ("VPD early flower", "1.0–1.5 kPa"),
                ("VPD late flower", "1.5–2.0 kPa"),
            ],
        )
        env_card.pack(fill="x", padx=5, pady=4)

        # Card 2 – Lighting
        light_card = self._make_info_card(
            right,
            "💡 Lighting",
            [
                ("Schedule", "12/12 (photoperiod); 12/12 or 18/6 (autoflower)"),
                ("PPFD", "600–900 µmol/m²/s; up to 1200 with CO₂"),
                ("DLI target", "35–45 mol/m²/d"),
                ("Light leaks", "Avoid any light during the dark period — causes hermaphrodites"),
            ],
        )
        light_card.pack(fill="x", padx=5, pady=4)

        # Card 3 – Nutrients
        nutes_card = self._make_info_card(
            right,
            "🌿 Nutrients",
            [
                ("Nitrogen", "Reduce N — excess causes dark green leaves, foxtails, harsh taste"),
                ("P+K boost", "Increase Phosphorus & Potassium throughout flower"),
                ("Wk 1–3 ratio", "2-3-3 (N-P-K)"),
                ("Wk 4+ ratio", "1-3-4 (N-P-K)"),
                ("Final 1–2 weeks", "FLUSH with plain pH'd water only"),
                ("EC range", "1.5–2.5 mS/cm; taper to 0 during flush"),
                ("pH (soil)", "6.0–7.0"),
                ("pH (hydro/coco)", "5.5–6.5"),
            ],
        )
        nutes_card.pack(fill="x", padx=5, pady=4)

        # Card 4 – Harvest Indicators
        harvest_card = self._make_info_card(
            right,
            "🔬 Harvest Indicators",
            [
                ("Pistils", "70–90% turned orange/red = mature"),
                ("Trichomes", "Requires jeweler's loupe (30–60×) or digital microscope"),
                ("All clear", "Immature — wait longer"),
                ("Mostly cloudy", "Peak THC — strong, cerebral effect"),
                ("20–30% amber", "THC degrading to CBN — heavier, more relaxing effect"),
                ("Calyxes", "Swelling and stacking indicate late flower"),
                ("Fan leaves", "Yellowing is normal senescence — not a deficiency"),
            ],
        )
        harvest_card.pack(fill="x", padx=5, pady=4)
