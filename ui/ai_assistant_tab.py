# FILE: growforge/ui/ai_assistant_tab.py
"""
GrowForge — AI Assistant tab connected to the self-contained GrowForge AI.
Features: contextual chat, symptom analysis, image triage, proactive alerts,
          feedback buttons (thumbs up/down + correction), AI self-improvement
          status panel, per-plant conversation memory, confidence scores.
"""

import customtkinter as ctk
from database import get_active_plants, get_row
from ai_assistant import GrowForgeAI

# Single global AI instance — persists across tab rebuilds
_ai_instance = None

def get_ai():
    global _ai_instance
    if _ai_instance is None:
        _ai_instance = GrowForgeAI()
    return _ai_instance


class AIAssistantTab:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.colors = app.colors
        self.ai = get_ai()
        self.selected_plant_id = None
        self.last_response_text = ""
        self.last_rule_id = ""
        self._build()

    def _build(self):
        main = ctk.CTkFrame(self.parent, fg_color="transparent")
        main.pack(fill="both", expand=True)
        main.grid_columnconfigure(0, weight=3)
        main.grid_columnconfigure(1, weight=1)
        main.grid_rowconfigure(0, weight=1)

        # ═══ LEFT: Chat Panel ═══════════════════════════════════════════
        chat_panel = ctk.CTkFrame(main, fg_color=self.colors["bg_secondary"], corner_radius=0)
        chat_panel.grid(row=0, column=0, sticky="nsew")
        chat_panel.grid_rowconfigure(1, weight=1)
        chat_panel.grid_columnconfigure(0, weight=1)

        # Header
        hdr = ctk.CTkFrame(chat_panel, fg_color=self.colors["bg_tertiary"], height=50, corner_radius=0)
        hdr.grid(row=0, column=0, sticky="ew")
        hdr.grid_propagate(False)
        hi = ctk.CTkFrame(hdr, fg_color="transparent")
        hi.pack(fill="x", padx=15, pady=10)

        ctk.CTkLabel(hi, text="🤖 GrowForge AI",
                     font=ctk.CTkFont(size=16, weight="bold"),
                     text_color=self.colors["fg_primary"]).pack(side="left")

        # Plant context selector
        plants = get_active_plants()
        plant_opts = ["No plant selected"] + [f"{p['name']} (#{p['id']})" for p in plants]
        self.plant_var = ctk.StringVar(value="No plant selected")
        ctk.CTkOptionMenu(hi, values=plant_opts, variable=self.plant_var,
                          width=200, command=self._on_plant_change).pack(side="right")
        ctk.CTkLabel(hi, text="Plant:", font=ctk.CTkFont(size=11),
                    text_color=self.colors["fg_muted"]).pack(side="right", padx=5)

        # Chat messages area
        self.chat_scroll = ctk.CTkScrollableFrame(
            chat_panel, fg_color="transparent",
            scrollbar_button_color=self.colors["bg_tertiary"])
        self.chat_scroll.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        # Welcome message
        try:
            welcome, conf = self.ai.chat_response("hello")
            self._add_bot_message(welcome, conf)
        except Exception:
            self._add_bot_message(
                "Welcome to GrowForge AI! I'm your local cultivation assistant. "
                "Ask me anything about growing — nutrients, pests, stages, VPD, and more.", 0.90)

        # Input bar
        input_bar = ctk.CTkFrame(chat_panel, fg_color=self.colors["bg_tertiary"], height=65, corner_radius=0)
        input_bar.grid(row=2, column=0, sticky="ew")
        inp = ctk.CTkFrame(input_bar, fg_color="transparent")
        inp.pack(fill="x", padx=15, pady=12)

        self.msg_entry = ctk.CTkEntry(inp, placeholder_text="Ask me anything about growing...",
                                       height=38, font=ctk.CTkFont(size=13))
        self.msg_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.msg_entry.bind("<Return>", lambda e: self._send())

        ctk.CTkButton(inp, text="📸 Describe", width=90, height=38, corner_radius=8,
                      fg_color=self.colors["accent_dark"], hover_color=self.colors["accent"],
                      font=ctk.CTkFont(size=11),
                      command=self._image_upload).pack(side="left", padx=(0, 5))

        ctk.CTkButton(inp, text="Send ➤", width=80, height=38, corner_radius=8,
                      fg_color=self.colors["accent"], hover_color=self.colors["accent_hover"],
                      command=self._send).pack(side="left")

        ctk.CTkButton(inp, text="🗑️", width=38, height=38, corner_radius=8,
                      fg_color=self.colors["bg_tertiary"], hover_color=self.colors["error"],
                      command=self._clear_chat).pack(side="right")

        # ═══ RIGHT: Sidebar ═════════════════════════════════════════════
        sidebar = ctk.CTkScrollableFrame(main, fg_color=self.colors["bg_card"],
                                          width=290, corner_radius=0,
                                          scrollbar_button_color=self.colors["bg_tertiary"])
        sidebar.grid(row=0, column=1, sticky="nsew")

        # ── AI Self-Improvement Status ──────────────────────────────────
        ctk.CTkLabel(sidebar, text="🧠 AI Self-Improvement",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=self.colors["fg_primary"]).pack(anchor="w", padx=12, pady=(15, 5))

        self.stats_frame = ctk.CTkFrame(sidebar, fg_color=self.colors["bg_secondary"], corner_radius=8)
        self.stats_frame.pack(fill="x", padx=10, pady=5)
        self._refresh_ai_stats()

        # ── Proactive Alerts ────────────────────────────────────────────
        ctk.CTkLabel(sidebar, text="⚡ Proactive Alerts",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=self.colors["fg_primary"]).pack(anchor="w", padx=12, pady=(15, 5))

        self.alerts_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        self.alerts_frame.pack(fill="x", padx=10)
        self._refresh_alerts()

        # ── Quick Topics ────────────────────────────────────────────────
        ctk.CTkLabel(sidebar, text="💡 Quick Topics",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=self.colors["fg_primary"]).pack(anchor="w", padx=12, pady=(15, 5))

        topics = [
            "How is my plant doing?", "What VPD should I target?",
            "My leaves are yellowing", "When should I harvest?",
            "Help with watering", "Nutrient feeding guide",
            "How to do LST", "Cloning basics",
            "What is topping?", "pH lockout info",
            "Spider mites help!", "Breeding basics",
        ]
        for label in topics:
            ctk.CTkButton(sidebar, text=label, height=28, anchor="w",
                          font=ctk.CTkFont(size=11),
                          fg_color=self.colors["bg_secondary"],
                          hover_color=self.colors["highlight"],
                          command=lambda q=label: self._quick_ask(q)).pack(fill="x", padx=10, pady=1)

        # ── Context panel ───────────────────────────────────────────────
        self.context_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        self.context_frame.pack(fill="x", padx=10, pady=(15, 10))

    # ────────────────────────────────────────────────────────────────────
    #  MESSAGING
    # ────────────────────────────────────────────────────────────────────

    def _clear_chat(self):
        """Clear all messages from the chat area."""
        for w in self.chat_scroll.winfo_children():
            w.destroy()
        self._add_bot_message(
            "Chat cleared. Ask me anything about growing!", 0.95)

    def _get_plant_id(self):
        val = self.plant_var.get()
        if val == "No plant selected":
            return None
        try:
            return int(val.split("#")[1].rstrip(")"))
        except (IndexError, ValueError):
            return None

    def _send(self):
        msg = self.msg_entry.get().strip()
        if not msg:
            return
        self._add_user_message(msg)
        self.msg_entry.delete(0, "end")

        pid = self._get_plant_id()
        response, confidence = self.ai.chat_response(msg, pid)
        self.last_response_text = response
        self._add_bot_message(response, confidence)

    def _quick_ask(self, query):
        self.msg_entry.delete(0, "end")
        self.msg_entry.insert(0, query)
        self._send()

    def _add_user_message(self, text):
        frame = ctk.CTkFrame(self.chat_scroll, fg_color=self.colors["accent_dark"], corner_radius=12)
        frame.pack(anchor="e", padx=15, pady=4, fill="x")
        ctk.CTkLabel(frame, text=text, font=ctk.CTkFont(size=12),
                     text_color=self.colors["fg_primary"],
                     wraplength=520, justify="left").pack(padx=12, pady=8, anchor="w")

    def _add_bot_message(self, text, confidence=0.75):
        frame = ctk.CTkFrame(self.chat_scroll, fg_color=self.colors["bg_card"], corner_radius=12)
        frame.pack(anchor="w", padx=15, pady=4, fill="x")
        inner = ctk.CTkFrame(frame, fg_color="transparent")
        inner.pack(fill="x", padx=12, pady=8)

        # Header with confidence
        hdr = ctk.CTkFrame(inner, fg_color="transparent")
        hdr.pack(fill="x")
        ctk.CTkLabel(hdr, text="🤖 GrowForge AI", font=ctk.CTkFont(size=11, weight="bold"),
                    text_color=self.colors["accent"]).pack(side="left")

        conf_pct = int(confidence * 100)
        conf_color = self.colors["success"] if conf_pct >= 80 else (
            self.colors["warning"] if conf_pct >= 60 else self.colors["fg_muted"])
        ctk.CTkLabel(hdr, text=f"{conf_pct}% confident",
                    font=ctk.CTkFont(size=9), text_color=conf_color).pack(side="right")

        # Message body
        ctk.CTkLabel(inner, text=text, font=ctk.CTkFont(size=12),
                     text_color=self.colors["fg_primary"],
                     wraplength=520, justify="left").pack(anchor="w", pady=(4, 0))

        # Feedback buttons
        fb = ctk.CTkFrame(inner, fg_color="transparent")
        fb.pack(fill="x", pady=(6, 0))

        response_ref = text[:200]  # capture for feedback

        ctk.CTkButton(fb, text="👍", width=35, height=26, corner_radius=6,
                      fg_color=self.colors["bg_secondary"], hover_color=self.colors["success"],
                      font=ctk.CTkFont(size=12),
                      command=lambda r=response_ref: self._feedback_thumbs_up(r)).pack(side="left", padx=(0, 3))

        ctk.CTkButton(fb, text="👎", width=35, height=26, corner_radius=6,
                      fg_color=self.colors["bg_secondary"], hover_color=self.colors["error"],
                      font=ctk.CTkFont(size=12),
                      command=lambda r=response_ref: self._feedback_thumbs_down(r)).pack(side="left", padx=(0, 3))

        ctk.CTkButton(fb, text="✏️ Correct", width=75, height=26, corner_radius=6,
                      fg_color=self.colors["bg_secondary"], hover_color=self.colors["highlight"],
                      font=ctk.CTkFont(size=10),
                      command=lambda r=response_ref: self._feedback_correct(r)).pack(side="left")

    # ────────────────────────────────────────────────────────────────────
    #  FEEDBACK
    # ────────────────────────────────────────────────────────────────────

    def _feedback_thumbs_up(self, response):
        pid = self._get_plant_id()
        self.ai.record_user_feedback(pid, response, 5, "positive")
        self._show_feedback_toast("👍 Thanks! This helps me improve.")
        self._refresh_ai_stats()

    def _feedback_thumbs_down(self, response):
        pid = self._get_plant_id()
        self.ai.record_user_feedback(pid, response, 1, "negative")
        self._show_feedback_toast("👎 Got it. Tell me what was wrong using '✏️ Correct'.")
        self._refresh_ai_stats()

    def _feedback_correct(self, response):
        dialog = ctk.CTkToplevel(self.parent)
        dialog.title("Correct the AI")
        dialog.geometry("450x320")
        dialog.transient(self.parent)
        dialog.after(50, lambda: dialog.grab_set())

        ctk.CTkLabel(dialog, text="✏️ Help me learn!",
                     font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(15, 5))
        ctk.CTkLabel(dialog, text="What was the correct answer or diagnosis?",
                     font=ctk.CTkFont(size=12)).pack(pady=5)

        correction_box = ctk.CTkTextbox(dialog, height=80, width=380)
        correction_box.pack(padx=20, pady=5)

        ctk.CTkLabel(dialog, text="Category:", font=ctk.CTkFont(size=12)).pack(pady=(5, 2))
        cat_var = ctk.StringVar(value="symptom_diagnosis")
        ctk.CTkOptionMenu(dialog, values=["symptom_diagnosis", "deficiency", "pest_disease",
                                           "watering", "nutrients_feeding", "stage_advice", "other"],
                          variable=cat_var, width=300).pack()

        def submit():
            correction = correction_box.get("1.0", "end-1c").strip()
            if correction:
                pid = self._get_plant_id()
                self.ai.record_user_feedback(
                    pid, response[:200], correction,
                    issue_type=cat_var.get(), outcome_details="user_correction")
                dialog.destroy()
                self._show_feedback_toast("✅ Learned! I'll use this to improve my future advice.")
                self._refresh_ai_stats()
            else:
                dialog.destroy()

        ctk.CTkButton(dialog, text="💾 Submit Correction", width=200, height=36,
                      fg_color=self.colors["accent"], command=submit).pack(pady=15)

    def _show_feedback_toast(self, text):
        toast = ctk.CTkFrame(self.chat_scroll, fg_color=self.colors["highlight"], corner_radius=8)
        toast.pack(anchor="w", padx=15, pady=2, fill="x")
        ctk.CTkLabel(toast, text=text, font=ctk.CTkFont(size=10),
                    text_color=self.colors["fg_primary"]).pack(padx=10, pady=5)

    # ────────────────────────────────────────────────────────────────────
    #  IMAGE TRIAGE
    # ────────────────────────────────────────────────────────────────────

    def _image_upload(self):
        self._add_user_message("📸 [Uploading photo for analysis...]")
        dialog = ctk.CTkToplevel(self.parent)
        dialog.title("Describe Your Photo")
        dialog.geometry("440x230")
        dialog.transient(self.parent)
        dialog.after(50, lambda: dialog.grab_set())

        ctk.CTkLabel(dialog, text="📸 Describe what you see in the photo:",
                     font=ctk.CTkFont(size=14, weight="bold")).pack(padx=20, pady=(15, 5))
        ctk.CTkLabel(dialog, text="(color changes, spots, curling, pests, which leaves, etc.)",
                     font=ctk.CTkFont(size=11), text_color=self.colors["fg_muted"]).pack(padx=20)

        desc = ctk.CTkEntry(dialog, placeholder_text="e.g., yellow lower leaves with green veins",
                             width=380, height=35)
        desc.pack(padx=20, pady=10)

        def analyze():
            d = desc.get()
            dialog.destroy()
            response = self.ai.triage_description(d)
            self._add_bot_message(response, 0.72)

        ctk.CTkButton(dialog, text="🔍 Analyze", width=150, height=36,
                      fg_color=self.colors["accent"], command=analyze).pack(pady=10)

    # ────────────────────────────────────────────────────────────────────
    #  SIDEBAR UPDATES
    # ────────────────────────────────────────────────────────────────────

    def _refresh_ai_stats(self):
        for w in self.stats_frame.winfo_children():
            w.destroy()
        stats = self.ai.get_improvement_stats()
        si = ctk.CTkFrame(self.stats_frame, fg_color="transparent")
        si.pack(fill="x", padx=10, pady=8)

        items = [
            ("💬 Interactions", str(stats["interactions"])),
            ("📝 Feedback received", str(stats["feedback_received"])),
            ("🧬 Rules self-coded", str(stats["rules_generated"])),
            ("⚖️ Weights adjusted", str(stats["weights_adjusted"])),
            ("🕐 Last improvement", stats["last_improvement"]),
        ]
        for label, value in items:
            row = ctk.CTkFrame(si, fg_color="transparent")
            row.pack(fill="x", pady=1)
            ctk.CTkLabel(row, text=label, font=ctk.CTkFont(size=10),
                        text_color=self.colors["fg_muted"]).pack(side="left")
            ctk.CTkLabel(row, text=value, font=ctk.CTkFont(size=10, weight="bold"),
                        text_color=self.colors["accent"]).pack(side="right")

    def _refresh_alerts(self):
        for w in self.alerts_frame.winfo_children():
            w.destroy()

        # Get alerts for all plants
        all_alerts = []
        for plant in get_active_plants():
            ctx = self.ai.get_context(plant["id"])
            alerts = self.ai.proactive_alerts(ctx)
            all_alerts.extend(alerts)

        if all_alerts:
            for alert in all_alerts[:8]:
                af = ctk.CTkFrame(self.alerts_frame, fg_color=self.colors["bg_secondary"], corner_radius=8)
                af.pack(fill="x", pady=2)
                ai = ctk.CTkFrame(af, fg_color="transparent")
                ai.pack(fill="x", padx=8, pady=6)
                icon = "⚠️" if alert["type"] == "warning" else "ℹ️"
                ctk.CTkLabel(ai, text=f"{icon} {alert.get('plant','')}",
                            font=ctk.CTkFont(size=10, weight="bold"),
                            text_color=self.colors["fg_primary"]).pack(anchor="w")
                ctk.CTkLabel(ai, text=alert["message"],
                            font=ctk.CTkFont(size=9), text_color=self.colors["fg_secondary"],
                            wraplength=230, justify="left").pack(anchor="w")
        else:
            ctk.CTkLabel(self.alerts_frame, text="✅ No alerts — looking good!",
                        font=ctk.CTkFont(size=11), text_color=self.colors["success"]).pack(pady=8)

    def _on_plant_change(self, *args):
        for w in self.context_frame.winfo_children():
            w.destroy()
        pid = self._get_plant_id()
        if not pid:
            return
        plant = get_row("plants", pid)
        if plant:
            ctk.CTkLabel(self.context_frame, text="🌱 Active Context",
                        font=ctk.CTkFont(size=12, weight="bold"),
                        text_color=self.colors["fg_primary"]).pack(anchor="w", pady=(5, 3))
            for line in [f"Stage: {plant.get('stage','?')}", f"Strain: {plant.get('strain_name','N/A')}",
                         f"Type: {plant.get('plant_type','N/A')}", f"Medium: {plant.get('medium','N/A')}"]:
                ctk.CTkLabel(self.context_frame, text=line, font=ctk.CTkFont(size=10),
                            text_color=self.colors["fg_muted"]).pack(anchor="w")
        self._refresh_alerts()
