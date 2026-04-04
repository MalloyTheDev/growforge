# FILE: growforge/ui/breeding_tab.py
"""
GrowForge — Breeding Lab tab: crosses, phenotype tracking, genetics guide.
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

    # ──────────────────────────────────────────────────────────────────────────
    # TOP-LEVEL BUILD
    # ──────────────────────────────────────────────────────────────────────────

    def _build(self):
        outer = ctk.CTkFrame(self.parent, fg_color="transparent")
        outer.pack(fill="both", expand=True)

        # ── Header ────────────────────────────────────────────────────
        header = ctk.CTkFrame(outer, fg_color="transparent")
        header.pack(fill="x", padx=25, pady=(20, 4))

        ctk.CTkLabel(header, text="🔬 Breeding Lab",
                     font=ctk.CTkFont(size=26, weight="bold"),
                     text_color=self.colors["fg_primary"]).pack(side="left")

        ctk.CTkLabel(header, text="Track crosses, score phenotypes, and select keepers",
                     font=ctk.CTkFont(size=13),
                     text_color=self.colors["fg_muted"]).pack(side="left", padx=(12, 0), pady=(6, 0))

        # ── Main Tab View ─────────────────────────────────────────────
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

        tabview.add("🧬 Crosses")
        tabview.add("📊 Phenotypes")
        tabview.add("📖 Genetics Guide")

        self._build_crosses_tab(tabview.tab("🧬 Crosses"))
        self._build_phenotypes_tab(tabview.tab("📊 Phenotypes"))
        self._build_guide_tab(tabview.tab("📖 Genetics Guide"))

    # ──────────────────────────────────────────────────────────────────────────
    # CROSSES TAB
    # ──────────────────────────────────────────────────────────────────────────

    def _build_crosses_tab(self, parent):
        scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent",
                                         scrollbar_button_color=self.colors["bg_tertiary"])
        scroll.pack(fill="both", expand=True, padx=0, pady=0)

        # Action buttons
        btn_row = ctk.CTkFrame(scroll, fg_color="transparent")
        btn_row.pack(fill="x", padx=10, pady=(10, 5))

        ctk.CTkButton(btn_row, text="➕ New Cross", width=130, height=36,
                      corner_radius=8, font=ctk.CTkFont(size=13),
                      fg_color=self.colors["accent"], hover_color=self.colors["accent_hover"],
                      command=self._new_cross_dialog).pack(side="left", padx=(0, 8))

        ctk.CTkButton(btn_row, text="📊 Score Phenotype", width=150, height=36,
                      corner_radius=8, font=ctk.CTkFont(size=13),
                      fg_color=self.colors["accent_dark"],
                      hover_color=self.colors["highlight"],
                      command=self._add_pheno_dialog).pack(side="left")

        # Separator
        sep = ctk.CTkFrame(scroll, height=1, fg_color=self.colors["border"])
        sep.pack(fill="x", padx=10, pady=(8, 10))

        crosses = get_crosses()
        if crosses:
            for cross in crosses:
                self._cross_card(scroll, cross)
        else:
            empty = ctk.CTkFrame(scroll, fg_color=self.colors["bg_card"], corner_radius=12)
            empty.pack(fill="x", padx=10, pady=20)
            ctk.CTkLabel(empty, text="🧬",
                        font=ctk.CTkFont(size=36)).pack(pady=(20, 4))
            ctk.CTkLabel(empty, text="No crosses recorded yet.",
                        font=ctk.CTkFont(size=14, weight="bold"),
                        text_color=self.colors["fg_primary"]).pack()
            ctk.CTkLabel(empty, text="Click 'New Cross' to record your first breeding project.",
                        font=ctk.CTkFont(size=12),
                        text_color=self.colors["fg_muted"]).pack(pady=(2, 20))

    # ──────────────────────────────────────────────────────────────────────────
    # PHENOTYPES TAB
    # ──────────────────────────────────────────────────────────────────────────

    def _build_phenotypes_tab(self, parent):
        scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent",
                                         scrollbar_button_color=self.colors["bg_tertiary"])
        scroll.pack(fill="both", expand=True)

        crosses = get_crosses()
        all_phenos = get_phenotypes()

        # Stats bar
        keepers = [p for p in all_phenos if p.get("is_keeper")]
        avg_score = (sum(p.get("overall_score", 0) for p in all_phenos) / len(all_phenos)) if all_phenos else 0

        stats_card = ctk.CTkFrame(scroll, fg_color=self.colors["bg_card"], corner_radius=12)
        stats_card.pack(fill="x", padx=10, pady=(10, 6))
        stats_inner = ctk.CTkFrame(stats_card, fg_color="transparent")
        stats_inner.pack(fill="x", padx=16, pady=12)

        stats_data = [
            ("🧬 Crosses", str(len(crosses))),
            ("📊 Phenotypes Scored", str(len(all_phenos))),
            ("⭐ Keepers", str(len(keepers))),
            ("📈 Average Score", f"{avg_score:.1f} / 10"),
        ]
        for label, value in stats_data:
            sf = ctk.CTkFrame(stats_inner, fg_color="transparent")
            sf.pack(side="left", expand=True)
            ctk.CTkLabel(sf, text=value,
                        font=ctk.CTkFont(size=22, weight="bold"),
                        text_color=self.colors["accent"]).pack()
            ctk.CTkLabel(sf, text=label,
                        font=ctk.CTkFont(size=10),
                        text_color=self.colors["fg_muted"]).pack()

        # Separator
        sep = ctk.CTkFrame(scroll, height=1, fg_color=self.colors["border"])
        sep.pack(fill="x", padx=10, pady=(4, 8))

        if not all_phenos:
            empty = ctk.CTkFrame(scroll, fg_color=self.colors["bg_card"], corner_radius=12)
            empty.pack(fill="x", padx=10, pady=10)
            ctk.CTkLabel(empty, text="📊",
                        font=ctk.CTkFont(size=36)).pack(pady=(20, 4))
            ctk.CTkLabel(empty, text="No phenotypes scored yet.",
                        font=ctk.CTkFont(size=14, weight="bold"),
                        text_color=self.colors["fg_primary"]).pack()
            ctk.CTkLabel(empty, text="Go to the Crosses tab and click 'Score Phenotype' to begin.",
                        font=ctk.CTkFont(size=12),
                        text_color=self.colors["fg_muted"]).pack(pady=(2, 20))
            return

        # Section headers
        ctk.CTkLabel(scroll, text="⭐ Keepers",
                    font=ctk.CTkFont(size=14, weight="bold"),
                    text_color=self.colors["fg_muted"]).pack(anchor="w", padx=12, pady=(4, 4))

        if keepers:
            for p in sorted(keepers, key=lambda x: x.get("overall_score", 0), reverse=True):
                self._pheno_card(scroll, p)
        else:
            ctk.CTkLabel(scroll, text="No keepers designated yet — score phenotypes and mark the best!",
                        font=ctk.CTkFont(size=11), text_color=self.colors["fg_muted"]).pack(anchor="w", padx=12, pady=4)

        sep2 = ctk.CTkFrame(scroll, height=1, fg_color=self.colors["border"])
        sep2.pack(fill="x", padx=10, pady=(10, 8))

        ctk.CTkLabel(scroll, text="All Phenotypes (by score)",
                    font=ctk.CTkFont(size=14, weight="bold"),
                    text_color=self.colors["fg_muted"]).pack(anchor="w", padx=12, pady=(4, 4))

        non_keepers = [p for p in all_phenos if not p.get("is_keeper")]
        for p in sorted(non_keepers, key=lambda x: x.get("overall_score", 0), reverse=True):
            self._pheno_card(scroll, p)

    def _pheno_card(self, parent, p):
        card = ctk.CTkFrame(parent, fg_color=self.colors["bg_card"], corner_radius=12)
        card.pack(fill="x", padx=10, pady=4)
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=14, pady=10)

        # Top row: name + score
        top = ctk.CTkFrame(inner, fg_color="transparent")
        top.pack(fill="x")

        keeper_icon = "⭐ " if p.get("is_keeper") else ""
        ctk.CTkLabel(top, text=f"{keeper_icon}{p['pheno_name']}",
                    font=ctk.CTkFont(size=14, weight="bold"),
                    text_color=self.colors["accent"] if p.get("is_keeper") else self.colors["fg_primary"]).pack(side="left")

        score = p.get("overall_score", 0)
        score_color = self.colors["success"] if score >= 7.5 else (self.colors["warning"] if score >= 5 else self.colors["error"])
        ctk.CTkLabel(top, text=f"{score:.1f} / 10",
                    font=ctk.CTkFont(size=13, weight="bold"),
                    text_color=score_color).pack(side="right")

        # Score bar
        bar = ctk.CTkProgressBar(inner, height=6, corner_radius=3,
                                  progress_color=score_color,
                                  fg_color=self.colors["bg_tertiary"])
        bar.set(score / 10)
        bar.pack(fill="x", pady=(4, 6))

        # Details row
        details = []
        if p.get("flowering_days"):
            details.append(f"🌸 {p['flowering_days']} days flower")
        if p.get("cross_name"):
            details.append(f"🧬 {p['cross_name']}")
        if details:
            ctk.CTkLabel(inner, text="  •  ".join(details),
                        font=ctk.CTkFont(size=11),
                        text_color=self.colors["fg_muted"]).pack(anchor="w")

        if p.get("notes"):
            ctk.CTkLabel(inner, text=p["notes"][:120],
                        font=ctk.CTkFont(size=11),
                        text_color=self.colors["fg_secondary"],
                        wraplength=600, justify="left").pack(anchor="w", pady=(2, 0))

    # ──────────────────────────────────────────────────────────────────────────
    # GENETICS GUIDE TAB
    # ──────────────────────────────────────────────────────────────────────────

    def _build_guide_tab(self, parent):
        scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent",
                                         scrollbar_button_color=self.colors["bg_tertiary"])
        scroll.pack(fill="both", expand=True)

        # ── Generation Roadmap ────────────────────────────────────────
        self._section_header(scroll, "🗺️ Generation Roadmap")

        roadmap_card = ctk.CTkFrame(scroll, fg_color=self.colors["bg_card"], corner_radius=12)
        roadmap_card.pack(fill="x", padx=10, pady=(0, 8))
        rm = ctk.CTkFrame(roadmap_card, fg_color="transparent")
        rm.pack(fill="x", padx=14, pady=12)

        generations = [
            ("P", "Parent", "#78909c",
             "The original parent strains. Choose stable, true-breeding varieties with complementary traits."),
            ("F1", "First Filial", self.colors["info"],
             "Cross of two P strains. All F1 plants are genetically identical — hybrid vigour is at its peak. Dominant traits are fully expressed. F1s are uniform but not stable for seed production."),
            ("F2", "Second Filial", self.colors["accent"],
             "Cross of two F1 siblings. Mendelian ratios emerge: 3:1 dominant-to-recessive for single-gene traits. High variation — ideal for phenotype hunting. Grow 20–50+ seeds to see full range of expression."),
            ("BX1/BX2", "Backcross", self.colors["warning"],
             "Cross F1 back to one of the original parents. Stabilises desired traits while retaining 75% (BX1) or 87.5% (BX2) parent genetics. Used to fix traits like potency, terpene profile, or structure."),
            ("S1", "Selfed / Reversed", "#ab47bc",
             "Pollen collected from a reversed (feminized via STS or CS spray) female plant is used to self-pollinate the same plant. Produces feminized seeds. Genetic variation is reduced — useful for preserving a specific phenotype."),
            ("IBL", "Inbred Line", self.colors["success"],
             "After F4–F6+ generations of consistent selection and self-pollination, plants become true-breeding. IBLs produce stable, predictable offspring and are the foundation of classic strain genetics."),
        ]

        for code, name, color, desc in generations:
            row = ctk.CTkFrame(rm, fg_color=self.colors["bg_secondary"], corner_radius=8)
            row.pack(fill="x", pady=3)
            ri = ctk.CTkFrame(row, fg_color="transparent")
            ri.pack(fill="x", padx=10, pady=8)

            badge = ctk.CTkLabel(ri, text=f"  {code}  ",
                                  font=ctk.CTkFont(size=11, weight="bold"),
                                  fg_color=color, text_color="#ffffff",
                                  corner_radius=6)
            badge.pack(side="left")

            txt = ctk.CTkFrame(ri, fg_color="transparent")
            txt.pack(side="left", padx=10, fill="x", expand=True)

            ctk.CTkLabel(txt, text=name,
                        font=ctk.CTkFont(size=12, weight="bold"),
                        text_color=self.colors["fg_primary"]).pack(anchor="w")
            ctk.CTkLabel(txt, text=desc,
                        font=ctk.CTkFont(size=11),
                        text_color=self.colors["fg_secondary"],
                        wraplength=650, justify="left").pack(anchor="w")

        # ── Mendelian Quick Reference ──────────────────────────────────
        self._section_header(scroll, "🔬 Mendelian Genetics Quick Reference")

        mendel_data = [
            ("F2 single-gene ratio", "3:1 dominant to recessive — e.g. 75% plants show dominant trait, 25% recessive"),
            ("F2 two-gene ratio", "9:3:3:1 (dihybrid cross) — four phenotype classes from two independent traits"),
            ("F2 minimum sample size", "Grow 20+ seeds for a reasonable sample; 50+ for statistically complete expression"),
            ("Incomplete dominance", "Some traits blend both parents — e.g. a medium-height plant from tall × short parents"),
            ("Epistasis", "One gene masks another — a plant may carry a trait but not express it until a later generation"),
            ("Dominant traits", "Usually visible in F1 — high THC, purple coloration (in many strains), early maturation"),
            ("Recessive traits", "Hidden in F1, emerge in F2/F3 — certain terpene profiles, CBD expression, dwarf growth"),
            ("Heritability", "Quantitative traits (yield, height) are polygenic — controlled by many genes, highly environment-influenced"),
        ]

        mendel_card = self._info_card(scroll, mendel_data)
        mendel_card.pack(fill="x", padx=10, pady=(0, 8))

        # ── Phenotype Hunting Strategy ────────────────────────────────
        self._section_header(scroll, "🔍 Phenotype Hunting Strategy")

        hunt_steps = [
            ("Step 1 — Germinate", "Start 10–20 seeds (F2 or BX) simultaneously for a fair comparison"),
            ("Step 2 — Veg notes", "Record vigor, internodal spacing, leaf shape, stem thickness, and smell"),
            ("Step 3 — Flip together", "Move all plants to 12/12 on the same day for direct comparison"),
            ("Step 4 — Score at week 6–8", "Score each plant on all 10 categories while buds are still forming"),
            ("Step 5 — Clone before harvest", "Take clones of every potential keeper in weeks 5–6 of flower"),
            ("Step 6 — Harvest & evaluate", "Weigh, dry, and cure each plant separately — taste and effect assessment"),
            ("Step 7 — Select keepers", "Choose 1–3 plants with complementary or outstanding trait profiles"),
            ("Step 8 — Verify", "Re-run your keeper 2+ times to confirm traits are consistent across environments"),
        ]

        hunt_card = self._info_card(scroll, hunt_steps)
        hunt_card.pack(fill="x", padx=10, pady=(0, 8))

        # ── Existing breeding guide (generation_guide from knowledge base) ──
        if BREEDING_GUIDE.get("generation_guide"):
            self._section_header(scroll, "📚 Classic Generation Reference")
            gen_card = ctk.CTkFrame(scroll, fg_color=self.colors["bg_card"], corner_radius=12)
            gen_card.pack(fill="x", padx=10, pady=(0, 12))
            gi = ctk.CTkFrame(gen_card, fg_color="transparent")
            gi.pack(fill="x", padx=14, pady=12)

            for gen, desc in BREEDING_GUIDE["generation_guide"].items():
                row = ctk.CTkFrame(gi, fg_color="transparent")
                row.pack(fill="x", pady=2)
                ctk.CTkLabel(row, text=f"  {gen}:",
                            font=ctk.CTkFont(size=12, weight="bold"),
                            text_color=self.colors["fg_primary"], width=60).pack(side="left")
                ctk.CTkLabel(row, text=desc,
                            font=ctk.CTkFont(size=11),
                            text_color=self.colors["fg_secondary"],
                            wraplength=650, justify="left").pack(side="left", padx=5)

    def _section_header(self, parent, title: str):
        ctk.CTkLabel(parent, text=title,
                    font=ctk.CTkFont(size=14, weight="bold"),
                    text_color=self.colors["fg_muted"]).pack(anchor="w", padx=12, pady=(10, 4))

    def _info_card(self, parent, rows: list) -> ctk.CTkFrame:
        card = ctk.CTkFrame(parent, fg_color=self.colors["bg_card"], corner_radius=12)
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=14, pady=10)
        for label, value in rows:
            row = ctk.CTkFrame(inner, fg_color="transparent")
            row.pack(fill="x", pady=2)
            ctk.CTkLabel(row, text=f"{label}:",
                        font=ctk.CTkFont(size=11, weight="bold"),
                        text_color=self.colors["fg_secondary"]).pack(side="left", anchor="nw", padx=(0, 6))
            ctk.CTkLabel(row, text=value,
                        font=ctk.CTkFont(size=11),
                        text_color=self.colors["fg_secondary"],
                        wraplength=640, justify="left").pack(side="left", anchor="nw", fill="x", expand=True)
        return card

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
