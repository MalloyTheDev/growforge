# FILE: growforge/ui/cloning_tab.py
"""
GrowForge — Cloning Station tab: mother management, clone batches, tracking, guide.
"""

import customtkinter as ctk
from datetime import datetime
from database import (
    get_mother_plants, get_clone_batches, get_clones_in_batch,
    insert_row, update_row, delete_row, get_active_plants,
)
from config import ROOTING_METHODS, CLONE_STAGES
from knowledge_base import CLONING_GUIDE
from ui.helpers import safe_int, validate_not_empty, show_validation_error, extract_id_from_option


class CloningTab:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.colors = app.colors
        self._build()

    # ──────────────────────────────────────────────────────────────────────────
    # TOP-LEVEL BUILD
    # ──────────────────────────────────────────────────────────────────────────

    def _build(self):
        outer = ctk.CTkFrame(self.parent, fg_color="transparent")
        outer.pack(fill="both", expand=True)

        # Header
        header = ctk.CTkFrame(outer, fg_color="transparent")
        header.pack(fill="x", padx=25, pady=(20, 4))

        ctk.CTkLabel(header, text="🧬 Cloning Station",
                     font=ctk.CTkFont(size=26, weight="bold"),
                     text_color=self.colors["fg_primary"]).pack(side="left")

        ctk.CTkLabel(header, text="Manage mothers, batches, and clone development",
                     font=ctk.CTkFont(size=13),
                     text_color=self.colors["fg_muted"]).pack(side="left", padx=(12, 0), pady=(6, 0))

        # Main tab view
        tabview = ctk.CTkTabview(
            outer,
            fg_color=self.colors["bg_secondary"],
            segmented_button_fg_color=self.colors["bg_tertiary"],
            segmented_button_selected_color=self.colors["accent_dark"],
            segmented_button_selected_hover_color=self.colors["accent"],
            segmented_button_unselected_color=self.colors["bg_tertiary"],
            segmented_button_unselected_hover_color=self.colors["highlight"],
            text_color=self.colors["fg_secondary"],
        )
        tabview.pack(fill="both", expand=True, padx=15, pady=(8, 15))

        tabview.add("👑 Mothers")
        tabview.add("🌿 Batches")
        tabview.add("📖 Guide")

        self._build_mothers_tab(tabview.tab("👑 Mothers"))
        self._build_batches_tab(tabview.tab("🌿 Batches"))
        self._build_guide_tab(tabview.tab("📖 Guide"))

    # ──────────────────────────────────────────────────────────────────────────
    # MOTHERS TAB
    # ──────────────────────────────────────────────────────────────────────────

    def _build_mothers_tab(self, parent):
        scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent",
                                         scrollbar_button_color=self.colors["bg_tertiary"])
        scroll.pack(fill="both", expand=True)

        btn_row = ctk.CTkFrame(scroll, fg_color="transparent")
        btn_row.pack(fill="x", padx=10, pady=(10, 6))

        ctk.CTkButton(btn_row, text="➕ New Batch", width=130, height=36,
                      corner_radius=8, font=ctk.CTkFont(size=13),
                      fg_color=self.colors["accent"], hover_color=self.colors["accent_hover"],
                      command=self._new_batch_dialog).pack(side="left")

        sep = ctk.CTkFrame(scroll, height=1, fg_color=self.colors["border"])
        sep.pack(fill="x", padx=10, pady=(4, 10))

        mothers = get_mother_plants()
        if mothers:
            for m in mothers:
                card = ctk.CTkFrame(scroll, fg_color=self.colors["bg_card"], corner_radius=12)
                card.pack(fill="x", padx=10, pady=4)
                inner = ctk.CTkFrame(card, fg_color="transparent")
                inner.pack(fill="x", padx=14, pady=12)

                # Name row
                top = ctk.CTkFrame(inner, fg_color="transparent")
                top.pack(fill="x")

                ctk.CTkLabel(top, text=f"👑 {m['name']}",
                            font=ctk.CTkFont(size=15, weight="bold"),
                            text_color=self.colors["fg_primary"]).pack(side="left")

                ctk.CTkButton(top, text="➕ New Batch", width=110, height=28,
                              font=ctk.CTkFont(size=11),
                              fg_color=self.colors["accent"],
                              hover_color=self.colors["accent_hover"],
                              command=self._new_batch_dialog).pack(side="right")

                strain = m.get("strain_name", "Unknown Strain")
                batches = get_clone_batches(m["id"])
                total_clones = sum(b.get("num_cuts", 0) for b in batches)
                active_clones = sum(
                    sum(1 for c in get_clones_in_batch(b["id"]) if c.get("status") == "Active")
                    for b in batches
                )

                details = f"{strain}  •  {len(batches)} batches  •  {total_clones} total cuts  •  {active_clones} active"
                ctk.CTkLabel(inner, text=details,
                            font=ctk.CTkFont(size=11),
                            text_color=self.colors["fg_muted"]).pack(anchor="w", pady=(4, 0))
        else:
            empty = ctk.CTkFrame(scroll, fg_color=self.colors["bg_card"], corner_radius=12)
            empty.pack(fill="x", padx=10, pady=20)
            ctk.CTkLabel(empty, text="👑", font=ctk.CTkFont(size=36)).pack(pady=(20, 4))
            ctk.CTkLabel(empty, text="No mother plants found.",
                        font=ctk.CTkFont(size=14, weight="bold"),
                        text_color=self.colors["fg_primary"]).pack()
            ctk.CTkLabel(empty, text="Open the Plants tab, edit a plant, and enable 'Is Mother Plant'.",
                        font=ctk.CTkFont(size=12),
                        text_color=self.colors["fg_muted"]).pack(pady=(2, 20))

    # ──────────────────────────────────────────────────────────────────────────
    # BATCHES TAB
    # ──────────────────────────────────────────────────────────────────────────

    def _build_batches_tab(self, parent):
        scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent",
                                         scrollbar_button_color=self.colors["bg_tertiary"])
        scroll.pack(fill="both", expand=True)

        # Optimal environment card at top
        env_card = ctk.CTkFrame(scroll, fg_color=self.colors["bg_card"], corner_radius=12)
        env_card.pack(fill="x", padx=10, pady=(10, 6))
        env_inner = ctk.CTkFrame(env_card, fg_color="transparent")
        env_inner.pack(fill="x", padx=14, pady=10)

        ctk.CTkLabel(env_inner, text="🌡️ Optimal Cloning Environment",
                    font=ctk.CTkFont(size=13, weight="bold"),
                    text_color=self.colors["accent"]).pack(anchor="w")

        sep = ctk.CTkFrame(env_inner, height=1, fg_color=self.colors["border"])
        sep.pack(fill="x", pady=(4, 6))

        env_rows = ctk.CTkFrame(env_inner, fg_color="transparent")
        env_rows.pack(fill="x")
        env_rows.grid_columnconfigure(0, weight=1)
        env_rows.grid_columnconfigure(1, weight=1)

        env_data_left = [
            ("Temperature", "72–78°F (22–26°C) — heat mat recommended"),
            ("RH Days 1–3", "90–100% — dome fully sealed"),
            ("RH Days 4–7", "70–80% — crack dome 30 min/day"),
            ("RH After Roots", "65–70% — remove dome gradually"),
        ]
        env_data_right = [
            ("Light Schedule", "18/6 — no intense direct light"),
            ("PPFD", "100–200 µmol/m²/s at 18–24 inches"),
            ("pH (water/gel)", "5.8–6.2"),
            ("Root Timeline", "Aero: 7–10 d | Rockwool: 10–14 d | Soil: 14–21 d"),
        ]

        for i, (label, value) in enumerate(env_data_left):
            rf = ctk.CTkFrame(env_rows, fg_color="transparent")
            rf.grid(row=i, column=0, sticky="w", padx=(0, 10), pady=1)
            ctk.CTkLabel(rf, text=f"{label}:",
                        font=ctk.CTkFont(size=11, weight="bold"),
                        text_color=self.colors["fg_secondary"]).pack(side="left", padx=(0, 4))
            ctk.CTkLabel(rf, text=value,
                        font=ctk.CTkFont(size=11),
                        text_color=self.colors["fg_secondary"]).pack(side="left")

        for i, (label, value) in enumerate(env_data_right):
            rf = ctk.CTkFrame(env_rows, fg_color="transparent")
            rf.grid(row=i, column=1, sticky="w", pady=1)
            ctk.CTkLabel(rf, text=f"{label}:",
                        font=ctk.CTkFont(size=11, weight="bold"),
                        text_color=self.colors["fg_secondary"]).pack(side="left", padx=(0, 4))
            ctk.CTkLabel(rf, text=value,
                        font=ctk.CTkFont(size=11),
                        text_color=self.colors["fg_secondary"],
                        wraplength=280).pack(side="left")

        # New batch button
        btn_row = ctk.CTkFrame(scroll, fg_color="transparent")
        btn_row.pack(fill="x", padx=10, pady=(8, 4))

        ctk.CTkButton(btn_row, text="➕ New Batch", width=130, height=36,
                      corner_radius=8, font=ctk.CTkFont(size=13),
                      fg_color=self.colors["accent"], hover_color=self.colors["accent_hover"],
                      command=self._new_batch_dialog).pack(side="left")

        sep2 = ctk.CTkFrame(scroll, height=1, fg_color=self.colors["border"])
        sep2.pack(fill="x", padx=10, pady=(4, 6))

        batches = get_clone_batches()
        if batches:
            for batch in batches:
                self._batch_card(scroll, batch)
        else:
            empty = ctk.CTkFrame(scroll, fg_color=self.colors["bg_card"], corner_radius=12)
            empty.pack(fill="x", padx=10, pady=10)
            ctk.CTkLabel(empty, text="🌿", font=ctk.CTkFont(size=36)).pack(pady=(20, 4))
            ctk.CTkLabel(empty, text="No clone batches yet.",
                        font=ctk.CTkFont(size=14, weight="bold"),
                        text_color=self.colors["fg_primary"]).pack()
            ctk.CTkLabel(empty, text="Click 'New Batch' to start tracking your clones.",
                        font=ctk.CTkFont(size=12),
                        text_color=self.colors["fg_muted"]).pack(pady=(2, 20))

    # ──────────────────────────────────────────────────────────────────────────
    # GUIDE TAB
    # ──────────────────────────────────────────────────────────────────────────

    def _build_guide_tab(self, parent):
        scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent",
                                         scrollbar_button_color=self.colors["bg_tertiary"])
        scroll.pack(fill="both", expand=True)

        # Step-by-step cutting procedure
        ctk.CTkLabel(scroll, text="✂️ Step-by-Step Cutting Procedure",
                    font=ctk.CTkFont(size=14, weight="bold"),
                    text_color=self.colors["fg_muted"]).pack(anchor="w", padx=12, pady=(10, 4))

        steps_card = ctk.CTkFrame(scroll, fg_color=self.colors["bg_card"], corner_radius=12)
        steps_card.pack(fill="x", padx=10, pady=(0, 8))
        steps_inner = ctk.CTkFrame(steps_card, fg_color="transparent")
        steps_inner.pack(fill="x", padx=14, pady=12)

        steps = [
            ("1", "Choose a healthy lower-mid branch from a well-established mother (4+ weeks in veg)"),
            ("2", "Select a branch with 2–3 nodes and 4–6 inches of stem length"),
            ("3", "Sterilize a sharp blade with isopropyl alcohol — a clean cut prevents infection"),
            ("4", "Make a 45° angled cut just below a node to maximize rooting surface area"),
            ("5", "Immediately place the cut end in clean water to prevent an air embolism"),
            ("6", "Strip all lower leaves and any growth tips — leave only 2–3 small upper fan leaves"),
            ("7", "Re-cut the stem 1/4 inch from the base while submerged in water"),
            ("8", "Dip or coat the bottom inch in rooting hormone (gel or powder)"),
            ("9", "Insert into pre-soaked rooting medium and seal under a humidity dome"),
            ("10", "Place under low-intensity light (18/6) — no direct intense light until roots form"),
        ]

        for num, text in steps:
            row = ctk.CTkFrame(steps_inner, fg_color=self.colors["bg_secondary"], corner_radius=6)
            row.pack(fill="x", pady=2)
            ri = ctk.CTkFrame(row, fg_color="transparent")
            ri.pack(fill="x", padx=10, pady=6)

            ctk.CTkLabel(ri, text=f" {num} ",
                        font=ctk.CTkFont(size=11, weight="bold"),
                        fg_color=self.colors["accent_dark"],
                        text_color="#ffffff", corner_radius=4).pack(side="left")
            ctk.CTkLabel(ri, text=text,
                        font=ctk.CTkFont(size=11),
                        text_color=self.colors["fg_secondary"],
                        wraplength=640, justify="left").pack(side="left", padx=(8, 0))

        # Mother plant selection
        ctk.CTkLabel(scroll, text="👑 Mother Plant Selection Criteria",
                    font=ctk.CTkFont(size=14, weight="bold"),
                    text_color=self.colors["fg_muted"]).pack(anchor="w", padx=12, pady=(12, 4))

        mother_card = ctk.CTkFrame(scroll, fg_color=self.colors["bg_card"], corner_radius=12)
        mother_card.pack(fill="x", padx=10, pady=(0, 8))
        mother_inner = ctk.CTkFrame(mother_card, fg_color="transparent")
        mother_inner.pack(fill="x", padx=14, pady=12)

        mother_tips = [
            ("Proven genetics", "Select from the 3rd harvest or later — genetics are confirmed by then"),
            ("Root development", "Strong, white, healthy roots in the medium"),
            ("Vigour", "Fast growth, tight internodal spacing, thick stems"),
            ("Pest & disease resistance", "Healthy mothers pass immunity traits to clones"),
            ("Light schedule", "Keep mothers on 18/6 veg schedule indefinitely"),
            ("Repotting", "Repot annually or when root-bound to prevent stress"),
            ("Maintenance cloning", "Take new cuts every 4–8 weeks to keep the mother vigorous"),
            ("Record keeping", "Document every batch taken, success rates, and health observations"),
        ]

        for label, value in mother_tips:
            row = ctk.CTkFrame(mother_inner, fg_color="transparent")
            row.pack(fill="x", pady=2)
            ctk.CTkLabel(row, text=f"• {label}:",
                        font=ctk.CTkFont(size=11, weight="bold"),
                        text_color=self.colors["fg_secondary"]).pack(side="left", anchor="nw", padx=(0, 4))
            ctk.CTkLabel(row, text=value,
                        font=ctk.CTkFont(size=11),
                        text_color=self.colors["fg_secondary"],
                        wraplength=580, justify="left").pack(side="left", anchor="nw")

        # Rooting method comparison
        ctk.CTkLabel(scroll, text="⚗️ Rooting Method Comparison",
                    font=ctk.CTkFont(size=14, weight="bold"),
                    text_color=self.colors["fg_muted"]).pack(anchor="w", padx=12, pady=(12, 4))

        method_card = ctk.CTkFrame(scroll, fg_color=self.colors["bg_card"], corner_radius=12)
        method_card.pack(fill="x", padx=10, pady=(0, 8))
        method_inner = ctk.CTkFrame(method_card, fg_color="transparent")
        method_inner.pack(fill="x", padx=14, pady=12)

        methods = [
            ("Aeroponic Cloner", "90–95%", "7–10 days", "Best results — roots in misted air. Higher upfront cost."),
            ("Rockwool + Clonex Gel", "80–90%", "10–14 days", "Reliable and widely used. Easy to monitor root development."),
            ("Rapid Rooter + Dome", "75–85%", "10–14 days", "Beginner-friendly plugs. Pre-moistened and ready to use."),
            ("Coco / Perlite + Dome", "70–85%", "10–18 days", "Reusable medium. Good drainage and aeration."),
            ("Water Cloning (plain)", "60–75%", "14–21 days", "Zero cost — simply suspend stems in a dark container of water."),
            ("Aloe Vera Gel (organic)", "70–80%", "14–21 days", "Natural rooting hormone alternative — fresh gel only."),
            ("Honey (organic)", "60–75%", "14–21 days", "Antibacterial coating — thin application on cut end only."),
        ]

        # Header row
        hdr = ctk.CTkFrame(method_inner, fg_color=self.colors["bg_tertiary"], corner_radius=6)
        hdr.pack(fill="x", pady=(0, 4))
        hi = ctk.CTkFrame(hdr, fg_color="transparent")
        hi.pack(fill="x", padx=10, pady=6)
        for col, weight in [("Method", 2), ("Success Rate", 1), ("Timeline", 1)]:
            ctk.CTkLabel(hi, text=col,
                        font=ctk.CTkFont(size=11, weight="bold"),
                        text_color=self.colors["fg_primary"]).pack(side="left", expand=True, anchor="w")

        for method, success, timeline, note in methods:
            row = ctk.CTkFrame(method_inner, fg_color=self.colors["bg_secondary"], corner_radius=6)
            row.pack(fill="x", pady=2)
            ri = ctk.CTkFrame(row, fg_color="transparent")
            ri.pack(fill="x", padx=10, pady=6)

            # Parse success rate for color
            try:
                rate = int(success.split("–")[0].replace("%", ""))
                s_color = self.colors["success"] if rate >= 80 else (self.colors["warning"] if rate >= 65 else self.colors["error"])
            except (ValueError, IndexError):
                s_color = self.colors["fg_muted"]

            ctk.CTkLabel(ri, text=method,
                        font=ctk.CTkFont(size=11, weight="bold"),
                        text_color=self.colors["fg_primary"],
                        width=180).pack(side="left", anchor="nw")
            ctk.CTkLabel(ri, text=success,
                        font=ctk.CTkFont(size=11, weight="bold"),
                        text_color=s_color,
                        width=80).pack(side="left", anchor="nw")
            ctk.CTkLabel(ri, text=timeline,
                        font=ctk.CTkFont(size=11),
                        text_color=self.colors["fg_muted"],
                        width=80).pack(side="left", anchor="nw")
            ctk.CTkLabel(ri, text=note,
                        font=ctk.CTkFont(size=11),
                        text_color=self.colors["fg_secondary"],
                        wraplength=350, justify="left").pack(side="left", anchor="nw")

        # Existing knowledge base guide sections
        for section, data in CLONING_GUIDE.items():
            if "title" not in data or "tips" not in data:
                continue
            gf = ctk.CTkFrame(scroll, fg_color=self.colors["bg_card"], corner_radius=12)
            gf.pack(fill="x", padx=10, pady=4)
            gi = ctk.CTkFrame(gf, fg_color="transparent")
            gi.pack(fill="x", padx=14, pady=10)
            ctk.CTkLabel(gi, text=data["title"],
                        font=ctk.CTkFont(size=13, weight="bold"),
                        text_color=self.colors["accent"]).pack(anchor="w")
            sep = ctk.CTkFrame(gi, height=1, fg_color=self.colors["border"])
            sep.pack(fill="x", pady=(4, 6))
            for tip in data["tips"][:5]:
                ctk.CTkLabel(gi, text=f"  • {tip}",
                            font=ctk.CTkFont(size=11),
                            text_color=self.colors["fg_secondary"],
                            wraplength=680, justify="left").pack(anchor="w", pady=1)

    def _batch_card(self, parent, batch):
        card = ctk.CTkFrame(parent, fg_color=self.colors["bg_card"], corner_radius=12)
        card.pack(fill="x", padx=10, pady=4)
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=14, pady=10)

        top = ctk.CTkFrame(inner, fg_color="transparent")
        top.pack(fill="x")

        ctk.CTkLabel(top, text=f"🌿 {batch['batch_name']}",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=self.colors["fg_primary"]).pack(side="left")

        ctk.CTkLabel(top, text=f"Cut: {batch.get('cut_date', 'N/A')}  •  {batch.get('num_cuts', 0)} cuts",
                     font=ctk.CTkFont(size=11),
                     text_color=self.colors["fg_muted"]).pack(side="right")

        details = []
        if batch.get("rooting_method"): details.append(batch["rooting_method"])
        if batch.get("medium"): details.append(batch["medium"])
        if details:
            ctk.CTkLabel(inner, text="  •  ".join(details),
                        font=ctk.CTkFont(size=11),
                        text_color=self.colors["fg_secondary"]).pack(anchor="w", pady=(3, 0))

        # Clone status summary + success rate
        clones = get_clones_in_batch(batch["id"])
        if clones:
            rooted = sum(1 for c in clones
                         if c.get("stage") in ("Rooted", "Transplanted", "Vegetative"))
            active = sum(1 for c in clones if c.get("status") == "Active")
            dead = sum(1 for c in clones if c.get("status") == "Dead")
            promoted = sum(1 for c in clones if c.get("status") == "Promoted")
            total = len(clones)

            summary_row = ctk.CTkFrame(inner, fg_color="transparent")
            summary_row.pack(fill="x", pady=(4, 0))

            summary_parts = []
            if active: summary_parts.append(f"🟢 {active} active")
            if dead: summary_parts.append(f"🔴 {dead} dead")
            if promoted: summary_parts.append(f"🔵 {promoted} promoted")
            if summary_parts:
                ctk.CTkLabel(summary_row, text="  ".join(summary_parts),
                            font=ctk.CTkFont(size=11),
                            text_color=self.colors["fg_primary"]).pack(side="left")

            # Success rate badge
            if total > 0:
                pct = int(rooted / total * 100)
                rate_color = self.colors["success"] if pct >= 75 else (
                    self.colors["warning"] if pct >= 50 else self.colors["error"])
                ctk.CTkLabel(summary_row, text=f"Root Success: {rooted}/{total} ({pct}%)",
                            font=ctk.CTkFont(size=11, weight="bold"),
                            text_color=rate_color).pack(side="right")

            # Individual clones
            clones_f = ctk.CTkFrame(inner, fg_color="transparent")
            clones_f.pack(fill="x", pady=(5, 0))

            for clone in clones:
                status_colors = {"Active": self.colors["success"],
                                  "Dead": self.colors["error"],
                                  "Promoted": self.colors["info"]}
                sc = status_colors.get(clone.get("status", ""), self.colors["fg_muted"])

                cf = ctk.CTkFrame(clones_f, fg_color=self.colors["bg_secondary"], corner_radius=6)
                cf.pack(fill="x", pady=1)
                ci = ctk.CTkFrame(cf, fg_color="transparent")
                ci.pack(fill="x", padx=10, pady=4)

                ctk.CTkLabel(ci, text=clone["clone_name"],
                            font=ctk.CTkFont(size=11),
                            text_color=self.colors["fg_primary"]).pack(side="left")
                ctk.CTkLabel(ci, text=f"{clone.get('stage', '?')}  •  {clone.get('status', '?')}",
                            font=ctk.CTkFont(size=10), text_color=sc).pack(side="right")

        # Action buttons
        btns = ctk.CTkFrame(inner, fg_color="transparent")
        btns.pack(fill="x", pady=(8, 0))

        ctk.CTkButton(btns, text="✏️ Update Clones", width=130, height=28,
                      corner_radius=6, font=ctk.CTkFont(size=11),
                      fg_color=self.colors["bg_tertiary"],
                      hover_color=self.colors["highlight"],
                      command=lambda b=batch: self._update_clones_dialog(b)).pack(side="left", padx=(0, 6))

        ctk.CTkButton(btns, text="🗑️ Delete Batch", width=110, height=28,
                      corner_radius=6, font=ctk.CTkFont(size=11),
                      fg_color=self.colors["bg_tertiary"],
                      hover_color=self.colors["error"],
                      text_color=self.colors["fg_muted"],
                      command=lambda b=batch: self._delete_batch(b)).pack(side="right")

    def _new_batch_dialog(self):
        dialog = ctk.CTkToplevel(self.parent)
        dialog.title("New Clone Batch")
        dialog.geometry("480x500")
        dialog.transient(self.parent)
        dialog.after(50, lambda: dialog.grab_set())

        scroll = ctk.CTkScrollableFrame(dialog, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(scroll, text="New Clone Batch", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(0, 15))

        mothers = get_mother_plants()
        all_plants = get_active_plants()
        source_options = [f"{p['name']} (#{p['id']})" for p in (mothers if mothers else all_plants)]

        if not source_options:
            ctk.CTkLabel(scroll, text="No plants available. Create a plant first.",
                        text_color=self.colors["error"]).pack(pady=20)
            return

        fields = {}

        ctk.CTkLabel(scroll, text="Batch Name", font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(8, 2))
        name_var = ctk.StringVar(value=f"Batch {datetime.now().strftime('%m/%d')}")
        ctk.CTkEntry(scroll, textvariable=name_var, width=380).pack(fill="x")
        fields["name"] = name_var

        ctk.CTkLabel(scroll, text="Mother / Source Plant", font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(8, 2))
        mother_var = ctk.StringVar(value=source_options[0])
        ctk.CTkOptionMenu(scroll, values=source_options, variable=mother_var, width=380).pack(fill="x")
        fields["mother"] = mother_var

        ctk.CTkLabel(scroll, text="Number of Cuts", font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(8, 2))
        cuts_var = ctk.StringVar(value="4")
        ctk.CTkEntry(scroll, textvariable=cuts_var, width=380).pack(fill="x")
        fields["cuts"] = cuts_var

        ctk.CTkLabel(scroll, text="Rooting Method", font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(8, 2))
        method_var = ctk.StringVar(value=ROOTING_METHODS[0])
        ctk.CTkOptionMenu(scroll, values=ROOTING_METHODS, variable=method_var, width=380).pack(fill="x")
        fields["method"] = method_var

        ctk.CTkLabel(scroll, text="Notes", font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(8, 2))
        notes = ctk.CTkTextbox(scroll, height=60, width=380)
        notes.pack(fill="x")

        self._batch_err = None

        def save():
            if self._batch_err:
                self._batch_err.destroy()
                self._batch_err = None

            batch_name = fields["name"].get().strip()
            err = validate_not_empty(batch_name, "Batch Name")
            if err:
                self._batch_err = show_validation_error(scroll, err, self.colors)
                return

            mother_id = extract_id_from_option(fields["mother"].get())
            if mother_id is None:
                self._batch_err = show_validation_error(scroll, "Select a valid mother plant.", self.colors)
                return

            num_cuts = safe_int(fields["cuts"].get(), 1)
            if num_cuts < 1:
                num_cuts = 1

            batch_id = insert_row("clone_batches", {
                "mother_plant_id": mother_id,
                "batch_name": fields["name"].get(),
                "cut_date": datetime.now().strftime("%Y-%m-%d"),
                "rooting_method": fields["method"].get(),
                "num_cuts": num_cuts,
                "notes": notes.get("1.0", "end-1c"),
            })

            # Create individual clone entries
            for i in range(1, num_cuts + 1):
                insert_row("clones", {
                    "batch_id": batch_id,
                    "clone_name": f"{fields['name'].get()} #{i}",
                    "stage": "Cut Taken",
                    "status": "Active",
                })

            dialog.destroy()
            self.app.refresh_current_tab()

        ctk.CTkButton(scroll, text="💾 Create Batch", height=40,
                      fg_color=self.colors["accent"], command=save).pack(fill="x", pady=(15, 5))

    def _update_clones_dialog(self, batch):
        dialog = ctk.CTkToplevel(self.parent)
        dialog.title(f"Update: {batch['batch_name']}")
        dialog.geometry("520x520")
        dialog.transient(self.parent)
        dialog.after(50, lambda: dialog.grab_set())

        scroll = ctk.CTkScrollableFrame(dialog, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(scroll, text=f"Update {batch['batch_name']}",
                     font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(0, 15))

        clones = get_clones_in_batch(batch["id"])
        clone_widgets = []

        for clone in clones:
            cf = ctk.CTkFrame(scroll, fg_color=self.colors["bg_card"], corner_radius=8)
            cf.pack(fill="x", pady=4)
            ci = ctk.CTkFrame(cf, fg_color="transparent")
            ci.pack(fill="x", padx=12, pady=8)

            top_row = ctk.CTkFrame(ci, fg_color="transparent")
            top_row.pack(fill="x")

            ctk.CTkLabel(top_row, text=clone["clone_name"],
                        font=ctk.CTkFont(size=13, weight="bold")).pack(side="left")

            # Delete individual clone
            ctk.CTkButton(top_row, text="🗑️", width=28, height=24,
                         font=ctk.CTkFont(size=10),
                         fg_color="transparent",
                         hover_color=self.colors["error"],
                         text_color=self.colors["fg_muted"],
                         command=lambda cid=clone["id"], d=dialog: self._delete_clone(cid, d)
                         ).pack(side="right")

            row = ctk.CTkFrame(ci, fg_color="transparent")
            row.pack(fill="x", pady=3)

            stage_var = ctk.StringVar(value=clone.get("stage", "Cut Taken"))
            ctk.CTkOptionMenu(row, values=CLONE_STAGES, variable=stage_var, width=180).pack(side="left", padx=(0, 10))

            status_var = ctk.StringVar(value=clone.get("status", "Active"))
            ctk.CTkOptionMenu(row, values=["Active", "Dead", "Promoted"], variable=status_var, width=120).pack(side="left")

            clone_widgets.append((clone["id"], stage_var, status_var))

        def save_all():
            now = datetime.now().strftime("%Y-%m-%d")
            for cid, stage_var, status_var in clone_widgets:
                data = {
                    "stage": stage_var.get(),
                    "status": status_var.get(),
                    "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }
                if stage_var.get() == "Rooted":
                    data["root_date"] = now
                elif stage_var.get() == "Transplanted":
                    data["transplant_date"] = now
                update_row("clones", cid, data)
            dialog.destroy()
            self.app.refresh_current_tab()

        ctk.CTkButton(scroll, text="💾 Save All", height=40,
                      fg_color=self.colors["accent"], command=save_all).pack(fill="x", pady=(15, 5))

    def _delete_clone(self, clone_id, parent_dialog):
        delete_row("clones", clone_id)
        parent_dialog.destroy()
        self.app.refresh_current_tab()

    def _delete_batch(self, batch):
        confirm = ctk.CTkToplevel(self.parent)
        confirm.title("Delete Batch")
        confirm.geometry("400x160")
        confirm.transient(self.parent)
        confirm.after(50, lambda: confirm.grab_set())

        ctk.CTkLabel(confirm, text=f"Delete '{batch['batch_name']}'?",
                    font=ctk.CTkFont(size=16, weight="bold"),
                    text_color=self.colors["fg_primary"]).pack(pady=(20, 5))

        clones = get_clones_in_batch(batch["id"])
        ctk.CTkLabel(confirm, text=f"This will also delete {len(clones)} clone(s).",
                    font=ctk.CTkFont(size=12),
                    text_color=self.colors["fg_muted"]).pack(pady=5)

        bf = ctk.CTkFrame(confirm, fg_color="transparent")
        bf.pack(pady=15)

        ctk.CTkButton(bf, text="Cancel", width=120,
                      fg_color=self.colors["bg_tertiary"],
                      command=confirm.destroy).pack(side="left", padx=10)

        def do_delete():
            # Delete all clones in batch first
            for clone in clones:
                delete_row("clones", clone["id"])
            delete_row("clone_batches", batch["id"])
            confirm.destroy()
            self.app.refresh_current_tab()

        ctk.CTkButton(bf, text="🗑️ Delete", width=120,
                      fg_color=self.colors["error"],
                      hover_color="#d32f2f",
                      command=do_delete).pack(side="left", padx=10)
