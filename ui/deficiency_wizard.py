# FILE: growforge/ui/deficiency_wizard.py
"""
GrowForge — Nutrient Deficiency & Pest Wizard: symptom → cause → fix.
"""

import customtkinter as ctk
from knowledge_base import NUTRIENT_ISSUES, PESTS, PH_LOCKOUT


class DeficiencyWizardTab:
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

        ctk.CTkLabel(header, text="🩺 Deficiency & Pest Wizard",
                     font=ctk.CTkFont(size=26, weight="bold"),
                     text_color=self.colors["fg_primary"]).pack(side="left")

        # ─── Symptom Selector ──────────────────────────────────────────
        wizard_card = ctk.CTkFrame(scroll, fg_color=self.colors["bg_card"], corner_radius=12)
        wizard_card.pack(fill="x", padx=25, pady=10)
        wi = ctk.CTkFrame(wizard_card, fg_color="transparent")
        wi.pack(fill="x", padx=18, pady=15)

        ctk.CTkLabel(wi, text="🔍 Select Symptoms to Diagnose",
                     font=ctk.CTkFont(size=16, weight="bold"),
                     text_color=self.colors["fg_primary"]).pack(anchor="w", pady=(0, 10))

        # Symptom categories
        symptoms = {
            "Leaf Color": [
                ("Yellowing (uniform, older leaves)", ["Nitrogen (N)"]),
                ("Yellowing (interveinal, older)", ["Magnesium (Mg)"]),
                ("Yellowing (new growth, green veins)", ["Iron (Fe)"]),
                ("Yellowing (new growth, uniform)", ["Sulfur (S)"]),
                ("Dark green / blue-green", ["Phosphorus (P)", "Nitrogen toxicity"]),
                ("Purple / red stems", ["Phosphorus (P)", "Genetics", "Cold"]),
                ("Brown / bronze patches", ["Phosphorus (P)", "Calcium (Ca)"]),
            ],
            "Leaf Edge / Tips": [
                ("Burnt crispy margins (edges)", ["Potassium (K)"]),
                ("Burnt tips only", ["Nutrient burn (overfeeding)"]),
                ("Curling up (taco)", ["Heat stress", "Light stress"]),
                ("Curling down (clawing)", ["Nitrogen toxicity", "Overwatering"]),
                ("Necrotic spots on tips", ["Calcium (Ca)"]),
            ],
            "New Growth": [
                ("Distorted / twisted new growth", ["Calcium (Ca)", "Zinc (Zn)", "Boron (B)"]),
                ("Very small new leaves", ["Zinc (Zn)"]),
                ("Growing tips dying", ["Boron (B)", "Calcium (Ca)"]),
                ("Bleached / white new growth", ["Light burn", "Iron (Fe) severe"]),
            ],
            "Whole Plant": [
                ("Slow / stunted growth", ["pH lockout", "Root bound", "Nitrogen (N)"]),
                ("Wilting (soil wet)", ["Overwatering", "Root rot"]),
                ("Wilting (soil dry)", ["Underwatering"]),
                ("Droopy overall", ["Overwatering", "Temperature stress"]),
                ("Stretching", ["Light too far / too dim"]),
            ],
            "Pests": [
                ("Tiny dots + webbing on undersides", ["Spider Mites"]),
                ("Small black flies near soil", ["Fungus Gnats"]),
                ("Silver / bronze streaks", ["Thrips"]),
                ("Clusters of small insects", ["Aphids"]),
                ("White powdery patches", ["Powdery Mildew"]),
                ("Gray mold inside buds", ["Bud Rot (Botrytis)"]),
                ("Brown slimy roots", ["Root Rot"]),
            ],
        }

        self.selected_symptoms = []
        self.result_frame = ctk.CTkFrame(scroll, fg_color="transparent")

        for category, symptom_list in symptoms.items():
            ctk.CTkLabel(wi, text=category,
                        font=ctk.CTkFont(size=13, weight="bold"),
                        text_color=self.colors["accent"]).pack(anchor="w", pady=(10, 3))

            for symptom_text, causes in symptom_list:
                var = ctk.BooleanVar(value=False)
                cb = ctk.CTkCheckBox(
                    wi, text=symptom_text, variable=var,
                    font=ctk.CTkFont(size=12),
                    command=lambda s=symptom_text, c=causes, v=var: self._toggle_symptom(s, c, v),
                )
                cb.pack(anchor="w", padx=15, pady=1)

        ctk.CTkButton(wi, text="🔍 Diagnose", height=38,
                      font=ctk.CTkFont(size=14), corner_radius=8,
                      fg_color=self.colors["accent"],
                      command=self._diagnose).pack(fill="x", pady=(15, 5))

        self.result_frame.pack(fill="x", padx=25, pady=10)

        # ─── Full Reference ────────────────────────────────────────────
        ctk.CTkLabel(scroll, text="📚 Full Nutrient Reference",
                     font=ctk.CTkFont(size=18, weight="bold"),
                     text_color=self.colors["fg_primary"]).pack(anchor="w", padx=25, pady=(20, 5))

        # pH lockout card
        ph_card = ctk.CTkFrame(scroll, fg_color=self.colors["bg_card"], corner_radius=10)
        ph_card.pack(fill="x", padx=25, pady=5)
        phi = ctk.CTkFrame(ph_card, fg_color="transparent")
        phi.pack(fill="x", padx=15, pady=12)

        ctk.CTkLabel(phi, text="⚗️ pH Lockout Zones",
                    font=ctk.CTkFont(size=14, weight="bold"),
                    text_color=self.colors["accent"]).pack(anchor="w")

        for medium, data in PH_LOCKOUT.items():
            opt = data["optimal"]
            ctk.CTkLabel(phi, text=f"\n{medium.upper()} — Optimal: {opt[0]}-{opt[1]}",
                        font=ctk.CTkFont(size=12, weight="bold"),
                        text_color=self.colors["fg_primary"]).pack(anchor="w")
            for zone, nutrients in data["lockout_zones"].items():
                ctk.CTkLabel(phi, text=f"  {zone.replace('_', ' ')}: {', '.join(nutrients)}",
                            font=ctk.CTkFont(size=11),
                            text_color=self.colors["fg_secondary"]).pack(anchor="w")

        # Nutrient cards
        for name, data in NUTRIENT_ISSUES.items():
            ncard = ctk.CTkFrame(scroll, fg_color=self.colors["bg_card"], corner_radius=10)
            ncard.pack(fill="x", padx=25, pady=4)
            ni = ctk.CTkFrame(ncard, fg_color="transparent")
            ni.pack(fill="x", padx=15, pady=10)

            mobility = "Mobile ↓" if data["mobile"] else "Immobile ↑"
            mob_color = self.colors["info"] if data["mobile"] else self.colors["warning"]

            top = ctk.CTkFrame(ni, fg_color="transparent")
            top.pack(fill="x")

            ctk.CTkLabel(top, text=f"🧪 {name}",
                        font=ctk.CTkFont(size=14, weight="bold"),
                        text_color=self.colors["fg_primary"]).pack(side="left")

            ctk.CTkLabel(top, text=f" {mobility} ",
                        font=ctk.CTkFont(size=10), text_color="#fff",
                        fg_color=mob_color, corner_radius=4).pack(side="right")

            if "deficiency" in data:
                d = data["deficiency"]
                ctk.CTkLabel(ni, text="Deficiency:",
                            font=ctk.CTkFont(size=12, weight="bold"),
                            text_color=self.colors["warning"]).pack(anchor="w", pady=(5, 2))
                for s in d["symptoms"][:4]:
                    ctk.CTkLabel(ni, text=f"  • {s}",
                                font=ctk.CTkFont(size=11),
                                text_color=self.colors["fg_secondary"],
                                wraplength=700, justify="left").pack(anchor="w")

                ctk.CTkLabel(ni, text="Fix:",
                            font=ctk.CTkFont(size=12, weight="bold"),
                            text_color=self.colors["success"]).pack(anchor="w", pady=(5, 2))
                for f in d["fix"][:3]:
                    ctk.CTkLabel(ni, text=f"  ✅ {f}",
                                font=ctk.CTkFont(size=11),
                                text_color=self.colors["fg_secondary"],
                                wraplength=700, justify="left").pack(anchor="w")

        # ─── Pest Reference ───────────────────────────────────────────
        ctk.CTkLabel(scroll, text="🐛 Pest & Disease Reference",
                     font=ctk.CTkFont(size=18, weight="bold"),
                     text_color=self.colors["fg_primary"]).pack(anchor="w", padx=25, pady=(20, 5))

        for pest_name, pest_data in PESTS.items():
            pcard = ctk.CTkFrame(scroll, fg_color=self.colors["bg_card"], corner_radius=10)
            pcard.pack(fill="x", padx=25, pady=4)
            pi = ctk.CTkFrame(pcard, fg_color="transparent")
            pi.pack(fill="x", padx=15, pady=10)

            sev_colors = {"Low": self.colors["success"], "Low-Medium": self.colors["info"],
                          "Medium": self.colors["warning"], "Medium-High": self.colors["warning"],
                          "High": self.colors["error"], "Critical": self.colors["error"]}

            top = ctk.CTkFrame(pi, fg_color="transparent")
            top.pack(fill="x")

            ctk.CTkLabel(top, text=f"🐛 {pest_name}",
                        font=ctk.CTkFont(size=14, weight="bold"),
                        text_color=self.colors["fg_primary"]).pack(side="left")

            sev = pest_data.get("severity", "Medium")
            ctk.CTkLabel(top, text=f" {sev} ",
                        font=ctk.CTkFont(size=10), text_color="#fff",
                        fg_color=sev_colors.get(sev, self.colors["warning"]),
                        corner_radius=4).pack(side="right")

            ctk.CTkLabel(pi, text="Signs:", font=ctk.CTkFont(size=12, weight="bold"),
                        text_color=self.colors["fg_secondary"]).pack(anchor="w", pady=(3, 1))
            for s in pest_data["signs"]:
                ctk.CTkLabel(pi, text=f"  • {s}", font=ctk.CTkFont(size=11),
                            text_color=self.colors["fg_secondary"]).pack(anchor="w")

            ctk.CTkLabel(pi, text="Treatment:", font=ctk.CTkFont(size=12, weight="bold"),
                        text_color=self.colors["success"]).pack(anchor="w", pady=(3, 1))
            for t in pest_data["treatment"][:4]:
                ctk.CTkLabel(pi, text=f"  ✅ {t}", font=ctk.CTkFont(size=11),
                            text_color=self.colors["fg_secondary"]).pack(anchor="w")

    def _toggle_symptom(self, symptom, causes, var):
        if var.get():
            self.selected_symptoms.append((symptom, causes))
        else:
            self.selected_symptoms = [(s, c) for s, c in self.selected_symptoms if s != symptom]

    def _diagnose(self):
        for w in self.result_frame.winfo_children():
            w.destroy()

        if not self.selected_symptoms:
            ctk.CTkLabel(self.result_frame, text="Please select at least one symptom above.",
                        text_color=self.colors["fg_muted"]).pack(pady=10)
            return

        # Count cause frequency
        cause_counts = {}
        for symptom, causes in self.selected_symptoms:
            for cause in causes:
                cause_counts[cause] = cause_counts.get(cause, 0) + 1

        sorted_causes = sorted(cause_counts.items(), key=lambda x: x[1], reverse=True)

        card = ctk.CTkFrame(self.result_frame, fg_color=self.colors["bg_card"], corner_radius=12)
        card.pack(fill="x", pady=5)
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=18, pady=15)

        ctk.CTkLabel(inner, text="🩺 Diagnosis Results",
                     font=ctk.CTkFont(size=18, weight="bold"),
                     text_color=self.colors["accent"]).pack(anchor="w", pady=(0, 10))

        ctk.CTkLabel(inner, text=f"Based on {len(self.selected_symptoms)} selected symptom(s):",
                    font=ctk.CTkFont(size=12),
                    text_color=self.colors["fg_muted"]).pack(anchor="w", pady=(0, 8))

        for i, (cause, count) in enumerate(sorted_causes):
            confidence = min(100, int(count / len(self.selected_symptoms) * 100))
            conf_color = self.colors["success"] if confidence > 60 else (
                self.colors["warning"] if confidence > 30 else self.colors["fg_muted"])

            rf = ctk.CTkFrame(inner, fg_color=self.colors["bg_secondary"], corner_radius=8)
            rf.pack(fill="x", pady=3)
            ri = ctk.CTkFrame(rf, fg_color="transparent")
            ri.pack(fill="x", padx=12, pady=8)

            ctk.CTkLabel(ri, text=f"#{i+1} {cause}",
                        font=ctk.CTkFont(size=13, weight="bold"),
                        text_color=self.colors["fg_primary"]).pack(side="left")

            ctk.CTkLabel(ri, text=f"{count} matching symptom(s)",
                        font=ctk.CTkFont(size=11),
                        text_color=conf_color).pack(side="right")

            # Show fix if it's a known nutrient issue
            for nut_name, nut_data in NUTRIENT_ISSUES.items():
                if cause.startswith(nut_name.split("(")[0].strip()):
                    if "deficiency" in nut_data and nut_data["deficiency"].get("fix"):
                        fix = nut_data["deficiency"]["fix"][0]
                        ctk.CTkLabel(ri, text=f"  ✅ Quick fix: {fix}",
                                    font=ctk.CTkFont(size=11),
                                    text_color=self.colors["success"]).pack(anchor="w")

            for pest_name, pest_data in PESTS.items():
                if cause == pest_name and pest_data.get("treatment"):
                    fix = pest_data["treatment"][0]
                    ctk.CTkLabel(ri, text=f"  ✅ Treatment: {fix}",
                                font=ctk.CTkFont(size=11),
                                text_color=self.colors["success"]).pack(anchor="w")

        ctk.CTkLabel(inner, text="\n💡 Always check pH first — it's the #1 cause of nutrient issues!",
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color=self.colors["info"]).pack(anchor="w", pady=(10, 0))
