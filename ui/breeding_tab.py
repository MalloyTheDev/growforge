# FILE: growforge/ui/breeding_tab.py
"""
GrowForge — Breeding Lab tab: crosses, phenotype tracking, genealogy, keepers.
"""

import customtkinter as ctk
from datetime import datetime
from database import (
    get_crosses, get_phenotypes, get_active_plants,
    insert_row,
)
from config import PHENO_SCORE_CATEGORIES
from knowledge_base import BREEDING_GUIDE
from ui.helpers import safe_int, validate_not_empty, show_validation_error, extract_id_from_option


class BreedingTab:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.colors = app.colors
        self._build()

    def _build(self):
        scroll = ctk.CTkScrollableFrame(self.parent, fg_color="transparent",
                                         scrollbar_button_color=self.colors["bg_tertiary"])
        scroll.pack(fill="both", expand=True)

        header = ctk.CTkFrame(scroll, fg_color="transparent")
        header.pack(fill="x", padx=25, pady=(20, 10))

        ctk.CTkLabel(header, text="🔬 Breeding Lab",
                     font=ctk.CTkFont(size=26, weight="bold"),
                     text_color=self.colors["fg_primary"]).pack(side="left")

        btn_frame = ctk.CTkFrame(header, fg_color="transparent")
        btn_frame.pack(side="right")

        ctk.CTkButton(btn_frame, text="➕ New Cross", width=130, height=36,
                      fg_color=self.colors["accent"], hover_color=self.colors["accent_hover"],
                      command=self._new_cross_dialog).pack(side="left", padx=5)

        ctk.CTkButton(btn_frame, text="📊 Add Phenotype", width=140, height=36,
                      fg_color=self.colors["accent_dark"],
                      command=self._add_pheno_dialog).pack(side="left")

        # ─── Crosses ───────────────────────────────────────────────────
        crosses = get_crosses()

        ctk.CTkLabel(scroll, text="🧬 Crosses",
                     font=ctk.CTkFont(size=18, weight="bold"),
                     text_color=self.colors["fg_primary"]).pack(anchor="w", padx=25, pady=(15, 5))

        if crosses:
            for cross in crosses:
                self._cross_card(scroll, cross)
        else:
            ctk.CTkLabel(scroll, text="No crosses recorded. Click 'New Cross' to start.",
                        text_color=self.colors["fg_muted"], font=ctk.CTkFont(size=12)).pack(padx=25, pady=10)

        # ─── Keepers ──────────────────────────────────────────────────
        all_phenos = get_phenotypes()
        keepers = [p for p in all_phenos if p.get("is_keeper")]

        ctk.CTkLabel(scroll, text="⭐ Keepers",
                     font=ctk.CTkFont(size=18, weight="bold"),
                     text_color=self.colors["fg_primary"]).pack(anchor="w", padx=25, pady=(20, 5))

        if keepers:
            for k in keepers:
                kf = ctk.CTkFrame(scroll, fg_color=self.colors["bg_card"], corner_radius=10)
                kf.pack(fill="x", padx=25, pady=3)
                ki = ctk.CTkFrame(kf, fg_color="transparent")
                ki.pack(fill="x", padx=15, pady=10)

                ctk.CTkLabel(ki, text=f"⭐ {k['pheno_name']}",
                            font=ctk.CTkFont(size=14, weight="bold"),
                            text_color=self.colors["accent"]).pack(side="left")

                ctk.CTkLabel(ki, text=f"Score: {k.get('overall_score', 0):.1f}/10 • {k.get('flowering_days', 0)} days flower",
                            font=ctk.CTkFont(size=11),
                            text_color=self.colors["fg_muted"]).pack(side="right")
        else:
            ctk.CTkLabel(scroll, text="No keepers yet. Score phenotypes and mark the best as keepers!",
                        text_color=self.colors["fg_muted"], font=ctk.CTkFont(size=12)).pack(padx=25, pady=10)

        # ─── Breeding Guide ───────────────────────────────────────────
        ctk.CTkLabel(scroll, text="📖 Breeding Guide",
                     font=ctk.CTkFont(size=18, weight="bold"),
                     text_color=self.colors["fg_primary"]).pack(anchor="w", padx=25, pady=(20, 5))

        # Generations table
        gen_card = ctk.CTkFrame(scroll, fg_color=self.colors["bg_card"], corner_radius=10)
        gen_card.pack(fill="x", padx=25, pady=5)
        gi = ctk.CTkFrame(gen_card, fg_color="transparent")
        gi.pack(fill="x", padx=15, pady=10)

        ctk.CTkLabel(gi, text="Generation Guide",
                    font=ctk.CTkFont(size=14, weight="bold"),
                    text_color=self.colors["accent"]).pack(anchor="w")

        for gen, desc in BREEDING_GUIDE.get("generation_guide", {}).items():
            row = ctk.CTkFrame(gi, fg_color="transparent")
            row.pack(fill="x", pady=1)
            ctk.CTkLabel(row, text=f"  {gen}:", font=ctk.CTkFont(size=12, weight="bold"),
                        text_color=self.colors["fg_primary"], width=50).pack(side="left")
            ctk.CTkLabel(row, text=desc, font=ctk.CTkFont(size=11),
                        text_color=self.colors["fg_secondary"],
                        wraplength=650, justify="left").pack(side="left", padx=5)

    def _cross_card(self, parent, cross):
        card = ctk.CTkFrame(parent, fg_color=self.colors["bg_card"], corner_radius=10)
        card.pack(fill="x", padx=25, pady=4)
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=15, pady=12)

        top = ctk.CTkFrame(inner, fg_color="transparent")
        top.pack(fill="x")

        ctk.CTkLabel(top, text=f"🧬 {cross['cross_name']}",
                     font=ctk.CTkFont(size=15, weight="bold"),
                     text_color=self.colors["fg_primary"]).pack(side="left")

        gen_badge = ctk.CTkLabel(top, text=f" {cross.get('generation', 'F1')} ",
                                 font=ctk.CTkFont(size=10, weight="bold"),
                                 text_color="#fff", fg_color=self.colors["info"],
                                 corner_radius=4)
        gen_badge.pack(side="right")

        parents = f"♀ {cross.get('mother_strain', '?')} × ♂ {cross.get('father_strain', '?')}"
        ctk.CTkLabel(inner, text=parents, font=ctk.CTkFont(size=12),
                    text_color=self.colors["fg_secondary"]).pack(anchor="w", pady=(3, 0))

        details = []
        if cross.get("pollination_date"): details.append(f"Pollinated: {cross['pollination_date']}")
        if cross.get("seed_count"): details.append(f"Seeds: {cross['seed_count']}")
        if cross.get("goals"): details.append(f"Goals: {cross['goals'][:80]}")

        if details:
            ctk.CTkLabel(inner, text=" • ".join(details),
                        font=ctk.CTkFont(size=11), text_color=self.colors["fg_muted"]).pack(anchor="w", pady=(2, 0))

        # Phenotypes for this cross
        phenos = get_phenotypes(cross["id"])
        if phenos:
            pf = ctk.CTkFrame(inner, fg_color="transparent")
            pf.pack(fill="x", pady=(5, 0))

            for p in phenos:
                keeper_icon = "⭐" if p.get("is_keeper") else "  "
                prow = ctk.CTkFrame(pf, fg_color=self.colors["bg_secondary"], corner_radius=6)
                prow.pack(fill="x", pady=1)
                pi = ctk.CTkFrame(prow, fg_color="transparent")
                pi.pack(fill="x", padx=10, pady=4)

                ctk.CTkLabel(pi, text=f"{keeper_icon} {p['pheno_name']}",
                            font=ctk.CTkFont(size=11), text_color=self.colors["fg_primary"]).pack(side="left")
                ctk.CTkLabel(pi, text=f"Score: {p.get('overall_score', 0):.1f}/10",
                            font=ctk.CTkFont(size=10), text_color=self.colors["accent"]).pack(side="right")

    def _new_cross_dialog(self):
        dialog = ctk.CTkToplevel(self.parent)
        dialog.title("New Cross")
        dialog.geometry("500x580")
        dialog.transient(self.parent)
        dialog.after(50, lambda: dialog.grab_set())

        scroll = ctk.CTkScrollableFrame(dialog, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(scroll, text="🧬 New Cross", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(0, 15))

        plants = get_active_plants()
        plant_options = ["(Manual Entry)"] + [f"{p['name']} (#{p['id']})" for p in plants]

        fields = {}

        def add_field(label, default="", options=None):
            ctk.CTkLabel(scroll, text=label, font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(8, 2))
            if options:
                var = ctk.StringVar(value=default or options[0])
                ctk.CTkOptionMenu(scroll, values=options, variable=var, width=400).pack(fill="x")
            else:
                var = ctk.StringVar(value=default)
                ctk.CTkEntry(scroll, textvariable=var, width=400).pack(fill="x")
            fields[label] = var

        add_field("Cross Name", "")
        add_field("Mother Plant", "", plant_options)
        add_field("Mother Strain", "")
        add_field("Father Plant", "", plant_options)
        add_field("Father Strain", "")
        add_field("Generation", "F1", ["F1", "F2", "F3", "F4", "BX1", "BX2", "S1"])
        add_field("Pollination Date", datetime.now().strftime("%Y-%m-%d"))
        add_field("Seed Count", "0")
        add_field("Goals", "")

        ctk.CTkLabel(scroll, text="Notes", font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(8, 2))
        notes = ctk.CTkTextbox(scroll, height=60, width=400)
        notes.pack(fill="x")

        self._cross_err = None

        def save():
            if self._cross_err:
                self._cross_err.destroy()
                self._cross_err = None

            cross_name = fields["Cross Name"].get().strip()
            err = validate_not_empty(cross_name, "Cross Name")
            if err:
                self._cross_err = show_validation_error(scroll, err, self.colors)
                return

            def get_plant_id(val):
                if val == "(Manual Entry)" or not val:
                    return None
                return extract_id_from_option(val)

            data = {
                "cross_name": cross_name,
                "mother_plant_id": get_plant_id(fields["Mother Plant"].get()),
                "father_plant_id": get_plant_id(fields["Father Plant"].get()),
                "mother_strain": fields["Mother Strain"].get(),
                "father_strain": fields["Father Strain"].get(),
                "generation": fields["Generation"].get(),
                "pollination_date": fields["Pollination Date"].get(),
                "seed_count": safe_int(fields["Seed Count"].get(), 0),
                "goals": fields["Goals"].get(),
                "notes": notes.get("1.0", "end-1c"),
            }
            insert_row("crosses", data)
            dialog.destroy()
            self.app.refresh_current_tab()

        ctk.CTkButton(scroll, text="💾 Save Cross", height=40,
                      fg_color=self.colors["accent"], command=save).pack(fill="x", pady=(15, 5))

    def _add_pheno_dialog(self):
        dialog = ctk.CTkToplevel(self.parent)
        dialog.title("Score Phenotype")
        dialog.geometry("520x700")
        dialog.transient(self.parent)
        dialog.after(50, lambda: dialog.grab_set())

        scroll = ctk.CTkScrollableFrame(dialog, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(scroll, text="📊 Score Phenotype", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(0, 15))

        crosses = get_crosses()
        cross_options = [f"{c['cross_name']} (#{c['id']})" for c in crosses] if crosses else ["(No crosses)"]

        plants = get_active_plants()
        plant_options = ["(None)"] + [f"{p['name']} (#{p['id']})" for p in plants]

        fields = {}

        ctk.CTkLabel(scroll, text="Cross", font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(5, 2))
        cross_var = ctk.StringVar(value=cross_options[0])
        ctk.CTkOptionMenu(scroll, values=cross_options, variable=cross_var, width=420).pack(fill="x")
        fields["cross"] = cross_var

        ctk.CTkLabel(scroll, text="Plant (optional)", font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(5, 2))
        plant_var = ctk.StringVar(value="(None)")
        ctk.CTkOptionMenu(scroll, values=plant_options, variable=plant_var, width=420).pack(fill="x")
        fields["plant"] = plant_var

        ctk.CTkLabel(scroll, text="Phenotype Name", font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(5, 2))
        name_var = ctk.StringVar()
        ctk.CTkEntry(scroll, textvariable=name_var, width=420).pack(fill="x")
        fields["name"] = name_var

        ctk.CTkLabel(scroll, text="Flowering Days", font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(5, 2))
        days_var = ctk.StringVar(value="60")
        ctk.CTkEntry(scroll, textvariable=days_var, width=420).pack(fill="x")
        fields["days"] = days_var

        # Score sliders
        score_vars = {}
        ctk.CTkLabel(scroll, text="\nScores (1-10)", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", pady=(10, 5))

        for cat in PHENO_SCORE_CATEGORIES:
            row = ctk.CTkFrame(scroll, fg_color="transparent")
            row.pack(fill="x", pady=2)

            ctk.CTkLabel(row, text=cat, font=ctk.CTkFont(size=11), width=140).pack(side="left")

            var = ctk.IntVar(value=5)
            slider = ctk.CTkSlider(row, from_=1, to=10, number_of_steps=9, variable=var, width=200)
            slider.pack(side="left", padx=5)

            val_label = ctk.CTkLabel(row, text="5", font=ctk.CTkFont(size=12, weight="bold"), width=30)
            val_label.pack(side="left")
            var.trace_add("write", lambda *a, v=var, l=val_label: l.configure(text=str(v.get())))

            score_vars[cat] = var

        # Keeper checkbox
        keeper_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(scroll, text="⭐ Mark as Keeper", variable=keeper_var).pack(anchor="w", pady=8)

        ctk.CTkLabel(scroll, text="Notes", font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(5, 2))
        notes = ctk.CTkTextbox(scroll, height=60, width=420)
        notes.pack(fill="x")

        self._pheno_err = None

        def save():
            if self._pheno_err:
                self._pheno_err.destroy()
                self._pheno_err = None

            pheno_name = fields["name"].get().strip()
            err = validate_not_empty(pheno_name, "Phenotype Name")
            if err:
                self._pheno_err = show_validation_error(scroll, err, self.colors)
                return

            def get_id(val):
                if "(None)" in val or "(No" in val:
                    return None
                return extract_id_from_option(val)

            scores = {cat.lower().replace(" ", "_") + "_score": var.get() for cat, var in score_vars.items()}
            overall = sum(scores.values()) / len(scores) if scores else 5.0

            fdays = safe_int(fields["days"].get(), 0)

            data = {
                "cross_id": get_id(fields["cross"].get()),
                "plant_id": get_id(fields["plant"].get()),
                "pheno_name": pheno_name,
                "vigor_score": score_vars["Vigor"].get(),
                "structure_score": score_vars["Structure"].get(),
                "yield_score": score_vars["Yield Potential"].get(),
                "terpene_score": score_vars["Terpene Profile"].get(),
                "resin_score": score_vars["Resin Production"].get(),
                "pest_resistance_score": score_vars["Pest Resistance"].get(),
                "mold_resistance_score": score_vars["Mold Resistance"].get(),
                "bag_appeal_score": score_vars["Bag Appeal"].get(),
                "potency_score": score_vars["Potency"].get(),
                "flavor_score": score_vars["Flavor"].get(),
                "overall_score": round(overall, 1),
                "is_keeper": 1 if keeper_var.get() else 0,
                "flowering_days": fdays,
                "notes": notes.get("1.0", "end-1c"),
            }
            insert_row("phenotypes", data)
            dialog.destroy()
            self.app.refresh_current_tab()

        ctk.CTkButton(scroll, text="💾 Save Phenotype", height=40,
                      fg_color=self.colors["accent"], command=save).pack(fill="x", pady=(15, 5))
