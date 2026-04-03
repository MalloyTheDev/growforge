# FILE: growforge/ui/tools_tab.py
"""
GrowForge — Tools tab: VPD calculator + chart, nutrient mixer,
yield estimator, training technique library.
"""

import customtkinter as ctk
import math
from utils.vpd_calculator import calculate_vpd, vpd_zone, vpd_color, c_to_f
from knowledge_base import TRAINING_TECHNIQUES

try:
    import matplotlib
    matplotlib.use("TkAgg")
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    import numpy as np
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False


class ToolsTab:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.colors = app.colors
        self._build()

    def _build(self):
        scroll = ctk.CTkScrollableFrame(self.parent, fg_color="transparent",
                                         scrollbar_button_color=self.colors["bg_tertiary"])
        scroll.pack(fill="both", expand=True)

        ctk.CTkLabel(scroll, text="🔧 Grower's Tools",
                     font=ctk.CTkFont(size=26, weight="bold"),
                     text_color=self.colors["fg_primary"]).pack(anchor="w", padx=25, pady=(20, 15))

        self._vpd_calculator(scroll)
        self._nutrient_mixer(scroll)
        self._yield_estimator(scroll)
        self._training_library(scroll)

    # ─── VPD Calculator ─────────────────────────────────────────────────
    def _vpd_calculator(self, parent):
        card = ctk.CTkFrame(parent, fg_color=self.colors["bg_card"], corner_radius=12)
        card.pack(fill="x", padx=25, pady=8)
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=18, pady=15)

        ctk.CTkLabel(inner, text="📊 VPD Calculator",
                     font=ctk.CTkFont(size=18, weight="bold"),
                     text_color=self.colors["fg_primary"]).pack(anchor="w", pady=(0, 10))

        controls = ctk.CTkFrame(inner, fg_color="transparent")
        controls.pack(fill="x")

        # Temperature
        temp_frame = ctk.CTkFrame(controls, fg_color="transparent")
        temp_frame.pack(side="left", padx=(0, 20))

        ctk.CTkLabel(temp_frame, text="Air Temp (°C)", font=ctk.CTkFont(size=12)).pack(anchor="w")
        self.temp_var = ctk.DoubleVar(value=25.0)
        temp_slider = ctk.CTkSlider(temp_frame, from_=15, to=35, variable=self.temp_var,
                                     width=200, number_of_steps=40,
                                     command=lambda _: self._update_vpd())
        temp_slider.pack()
        self.temp_label = ctk.CTkLabel(temp_frame, text="25.0°C (77.0°F)",
                                       font=ctk.CTkFont(size=11), text_color=self.colors["fg_muted"])
        self.temp_label.pack()

        # Humidity
        rh_frame = ctk.CTkFrame(controls, fg_color="transparent")
        rh_frame.pack(side="left", padx=20)

        ctk.CTkLabel(rh_frame, text="Humidity (%)", font=ctk.CTkFont(size=12)).pack(anchor="w")
        self.rh_var = ctk.DoubleVar(value=55.0)
        rh_slider = ctk.CTkSlider(rh_frame, from_=20, to=90, variable=self.rh_var,
                                   width=200, number_of_steps=70,
                                   command=lambda _: self._update_vpd())
        rh_slider.pack()
        self.rh_label = ctk.CTkLabel(rh_frame, text="55.0%",
                                      font=ctk.CTkFont(size=11), text_color=self.colors["fg_muted"])
        self.rh_label.pack()

        # Leaf offset
        offset_frame = ctk.CTkFrame(controls, fg_color="transparent")
        offset_frame.pack(side="left", padx=20)

        ctk.CTkLabel(offset_frame, text="Leaf Offset (°C)", font=ctk.CTkFont(size=12)).pack(anchor="w")
        self.offset_var = ctk.DoubleVar(value=2.0)
        ctk.CTkSlider(offset_frame, from_=0, to=5, variable=self.offset_var,
                      width=150, number_of_steps=10,
                      command=lambda _: self._update_vpd()).pack()
        self.offset_label = ctk.CTkLabel(offset_frame, text="2.0°C",
                                          font=ctk.CTkFont(size=11), text_color=self.colors["fg_muted"])
        self.offset_label.pack()

        # Result
        self.vpd_result = ctk.CTkLabel(inner, text="",
                                        font=ctk.CTkFont(size=28, weight="bold"))
        self.vpd_result.pack(pady=(15, 5))

        self.vpd_zone_label = ctk.CTkLabel(inner, text="",
                                            font=ctk.CTkFont(size=13))
        self.vpd_zone_label.pack()

        # VPD Chart
        if HAS_MATPLOTLIB:
            self.chart_frame = ctk.CTkFrame(inner, fg_color="transparent")
            self.chart_frame.pack(fill="x", pady=(15, 5))
            self._render_vpd_chart()

        self._update_vpd()

    def _update_vpd(self):
        temp = self.temp_var.get()
        rh = self.rh_var.get()
        offset = self.offset_var.get()

        vpd = calculate_vpd(temp, rh, offset)
        zone = vpd_zone(vpd)
        color = vpd_color(vpd)

        self.temp_label.configure(text=f"{temp:.1f}°C ({c_to_f(temp):.1f}°F)")
        self.rh_label.configure(text=f"{rh:.0f}%")
        self.offset_label.configure(text=f"{offset:.1f}°C")
        self.vpd_result.configure(text=f"VPD: {vpd:.2f} kPa", text_color=color)
        self.vpd_zone_label.configure(text=zone, text_color=color)

    def _render_vpd_chart(self):
        for w in self.chart_frame.winfo_children():
            w.destroy()

        fig = Figure(figsize=(7, 3.5), dpi=100)
        fig.patch.set_facecolor("#1a2e1a")
        ax = fig.add_subplot(111)
        ax.set_facecolor("#0f1a0f")

        temps = list(range(18, 33))
        rhs = list(range(30, 86, 5))

        data = []
        for t in temps:
            row = []
            for r in rhs:
                v = calculate_vpd(t, r, 2.0)
                row.append(v)
            data.append(row)

        import numpy as np
        data_arr = np.array(data)

        # Custom colormap
        from matplotlib.colors import LinearSegmentedColormap
        colors_list = ["#29b6f6", "#66bb6a", "#4caf50", "#8bc34a", "#ffc107", "#ff9800", "#f44336"]
        cmap = LinearSegmentedColormap.from_list("vpd", colors_list, N=256)

        im = ax.imshow(data_arr, cmap=cmap, aspect="auto", vmin=0.2, vmax=2.0,
                       extent=[rhs[0], rhs[-1], temps[-1], temps[0]])

        ax.set_xlabel("Relative Humidity (%)", color="#a8c8a8", fontsize=9)
        ax.set_ylabel("Temperature (°C)", color="#a8c8a8", fontsize=9)
        ax.set_title("VPD Chart (kPa)", color="#e8f5e8", fontsize=11, fontweight="bold")
        ax.tick_params(colors="#6a8a6a", labelsize=8)

        cbar = fig.colorbar(im, ax=ax, pad=0.02)
        cbar.ax.tick_params(colors="#6a8a6a", labelsize=8)
        cbar.set_label("VPD (kPa)", color="#a8c8a8", fontsize=9)

        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="x")

    # ─── Nutrient Mixer ──────────────────────────────────────────────────
    def _nutrient_mixer(self, parent):
        card = ctk.CTkFrame(parent, fg_color=self.colors["bg_card"], corner_radius=12)
        card.pack(fill="x", padx=25, pady=8)
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=18, pady=15)

        ctk.CTkLabel(inner, text="🧪 Nutrient Mixing Calculator",
                     font=ctk.CTkFont(size=18, weight="bold"),
                     text_color=self.colors["fg_primary"]).pack(anchor="w", pady=(0, 10))

        controls = ctk.CTkFrame(inner, fg_color="transparent")
        controls.pack(fill="x")

        # Water volume
        ctk.CTkLabel(controls, text="Water Volume (L):", font=ctk.CTkFont(size=12)).pack(side="left")
        self.water_vol = ctk.StringVar(value="10")
        ctk.CTkEntry(controls, textvariable=self.water_vol, width=80).pack(side="left", padx=5)

        ctk.CTkLabel(controls, text="  Nutrient (ml/L):", font=ctk.CTkFont(size=12)).pack(side="left", padx=(20, 0))
        self.ml_per_l = ctk.StringVar(value="2.5")
        ctk.CTkEntry(controls, textvariable=self.ml_per_l, width=80).pack(side="left", padx=5)

        ctk.CTkButton(controls, text="Calculate", width=100, height=30,
                      fg_color=self.colors["accent"],
                      command=self._calc_nutrients).pack(side="left", padx=10)

        self.nutrient_result = ctk.CTkLabel(inner, text="",
                                             font=ctk.CTkFont(size=14),
                                             text_color=self.colors["accent"])
        self.nutrient_result.pack(anchor="w", pady=(10, 0))

        # Quick reference
        ctk.CTkLabel(inner, text="\n📋 Common Nutrient Ratios:",
                    font=ctk.CTkFont(size=13, weight="bold"),
                    text_color=self.colors["fg_primary"]).pack(anchor="w", pady=(5, 3))

        ratios = [
            "Seedling: 1/4 strength (0.5-1.0 ml/L typical)",
            "Veg: Full strength (2-4 ml/L) — Higher N ratio (3-1-2)",
            "Flower: Full strength (2-4 ml/L) — Higher PK ratio (1-3-2)",
            "Cal-Mag: 2-5 ml/L (LED grows, coco, RO water)",
            "Flush: 0 ml/L — plain pH'd water",
        ]
        for r in ratios:
            ctk.CTkLabel(inner, text=f"  • {r}", font=ctk.CTkFont(size=11),
                        text_color=self.colors["fg_secondary"]).pack(anchor="w")

    def _calc_nutrients(self):
        try:
            vol = float(self.water_vol.get())
            ml = float(self.ml_per_l.get())
            total = vol * ml
            self.nutrient_result.configure(
                text=f"💧 Add {total:.1f} ml of nutrient to {vol:.1f}L of water"
            )
        except ValueError:
            self.nutrient_result.configure(text="⚠️ Enter valid numbers")

    # ─── Yield Estimator ─────────────────────────────────────────────────
    def _yield_estimator(self, parent):
        card = ctk.CTkFrame(parent, fg_color=self.colors["bg_card"], corner_radius=12)
        card.pack(fill="x", padx=25, pady=8)
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=18, pady=15)

        ctk.CTkLabel(inner, text="⚖️ Yield Estimator",
                     font=ctk.CTkFont(size=18, weight="bold"),
                     text_color=self.colors["fg_primary"]).pack(anchor="w", pady=(0, 10))

        ctk.CTkLabel(inner, text="Rough estimate based on light wattage (results vary widely)",
                    font=ctk.CTkFont(size=11), text_color=self.colors["fg_muted"]).pack(anchor="w")

        controls = ctk.CTkFrame(inner, fg_color="transparent")
        controls.pack(fill="x", pady=10)

        ctk.CTkLabel(controls, text="Light Wattage:", font=ctk.CTkFont(size=12)).pack(side="left")
        self.wattage_var = ctk.StringVar(value="400")
        ctk.CTkEntry(controls, textvariable=self.wattage_var, width=80).pack(side="left", padx=5)

        ctk.CTkLabel(controls, text="  Light Type:", font=ctk.CTkFont(size=12)).pack(side="left", padx=(15, 0))
        self.light_eff = ctk.StringVar(value="LED (1.5 g/W)")
        ctk.CTkOptionMenu(controls, values=[
            "LED (1.5 g/W)", "HPS (1.0 g/W)", "CMH (1.2 g/W)", "CFL (0.5 g/W)"
        ], variable=self.light_eff, width=160).pack(side="left", padx=5)

        ctk.CTkLabel(controls, text="  Skill:", font=ctk.CTkFont(size=12)).pack(side="left", padx=(15, 0))
        self.skill_var = ctk.StringVar(value="Intermediate (0.8x)")
        ctk.CTkOptionMenu(controls, values=[
            "Beginner (0.5x)", "Intermediate (0.8x)", "Advanced (1.0x)", "Expert (1.2x)"
        ], variable=self.skill_var, width=160).pack(side="left", padx=5)

        ctk.CTkButton(controls, text="Estimate", width=100, height=30,
                      fg_color=self.colors["accent"],
                      command=self._calc_yield).pack(side="left", padx=10)

        self.yield_result = ctk.CTkLabel(inner, text="",
                                          font=ctk.CTkFont(size=16, weight="bold"),
                                          text_color=self.colors["accent"])
        self.yield_result.pack(anchor="w", pady=(5, 0))

    def _calc_yield(self):
        try:
            wattage = float(self.wattage_var.get())
            gpw_map = {"LED": 1.5, "HPS": 1.0, "CMH": 1.2, "CFL": 0.5}
            light_str = self.light_eff.get()
            gpw = 1.0
            for k, v in gpw_map.items():
                if k in light_str:
                    gpw = v
                    break

            skill_map = {"Beginner": 0.5, "Intermediate": 0.8, "Advanced": 1.0, "Expert": 1.2}
            skill_mult = 0.8
            for k, v in skill_map.items():
                if k in self.skill_var.get():
                    skill_mult = v
                    break

            est = wattage * gpw * skill_mult
            low = est * 0.7
            high = est * 1.3

            self.yield_result.configure(
                text=f"🌾 Estimated yield: {low:.0f}g – {high:.0f}g (avg: {est:.0f}g dry)"
            )
        except ValueError:
            self.yield_result.configure(text="⚠️ Enter valid wattage")

    # ─── Training Library ────────────────────────────────────────────────
    def _training_library(self, parent):
        ctk.CTkLabel(parent, text="✂️ Training Technique Library",
                     font=ctk.CTkFont(size=18, weight="bold"),
                     text_color=self.colors["fg_primary"]).pack(anchor="w", padx=25, pady=(15, 5))

        for name, data in TRAINING_TECHNIQUES.items():
            card = ctk.CTkFrame(parent, fg_color=self.colors["bg_card"], corner_radius=10)
            card.pack(fill="x", padx=25, pady=4)
            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(fill="x", padx=15, pady=10)

            top = ctk.CTkFrame(inner, fg_color="transparent")
            top.pack(fill="x")

            ctk.CTkLabel(top, text=f"✂️ {name}",
                        font=ctk.CTkFont(size=14, weight="bold"),
                        text_color=self.colors["fg_primary"]).pack(side="left")

            auto_text = "✅ Auto-safe" if data["auto_safe"] else "❌ Not for autos"
            auto_color = self.colors["success"] if data["auto_safe"] else self.colors["error"]
            ctk.CTkLabel(top, text=auto_text, font=ctk.CTkFont(size=10),
                        text_color=auto_color).pack(side="right")

            ctk.CTkLabel(top, text=f"{data['difficulty']} • {data['stage']}",
                        font=ctk.CTkFont(size=11),
                        text_color=self.colors["fg_muted"]).pack(side="right", padx=10)

            ctk.CTkLabel(inner, text=data["description"],
                        font=ctk.CTkFont(size=11),
                        text_color=self.colors["fg_secondary"],
                        wraplength=750, justify="left").pack(anchor="w", pady=(5, 3))

            steps_text = " → ".join(data["steps"][:4])
            ctk.CTkLabel(inner, text=f"Steps: {steps_text}",
                        font=ctk.CTkFont(size=10),
                        text_color=self.colors["fg_muted"],
                        wraplength=750, justify="left").pack(anchor="w")
