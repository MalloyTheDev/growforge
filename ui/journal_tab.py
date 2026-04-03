# FILE: growforge/ui/journal_tab.py
"""
GrowForge — Grow Journal tab with event log, filtering, add/delete, and photo timeline.
"""

import customtkinter as ctk
from datetime import datetime
from database import (
    get_recent_events, get_active_plants, get_plant_events,
    search_events, insert_row, delete_row,
)
from config import EVENT_TYPES
from ui.helpers import (
    validate_not_empty, show_validation_error, extract_id_from_option,
)


class JournalTab:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.colors = app.colors
        self._build()

    def _build(self):
        # Top bar with filters
        top = ctk.CTkFrame(self.parent, fg_color=self.colors["bg_secondary"], height=60, corner_radius=0)
        top.pack(fill="x")
        top.pack_propagate(False)

        inner_top = ctk.CTkFrame(top, fg_color="transparent")
        inner_top.pack(fill="x", padx=25, pady=10)

        ctk.CTkLabel(inner_top, text="📓 Grow Journal",
                     font=ctk.CTkFont(size=22, weight="bold"),
                     text_color=self.colors["fg_primary"]).pack(side="left")

        # Add Event button
        ctk.CTkButton(
            inner_top, text="➕ New Entry", width=120, height=32,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=self.colors["accent"],
            hover_color=self.colors["accent_hover"],
            corner_radius=8,
            command=self._add_event_dialog,
        ).pack(side="left", padx=(15, 0))

        # Search
        self.search_var = ctk.StringVar()
        search_entry = ctk.CTkEntry(inner_top, textvariable=self.search_var,
                                     placeholder_text="🔍 Search events...", width=200)
        search_entry.pack(side="right", padx=(10, 0))
        search_entry.bind("<Return>", lambda e: self._search())

        # Plant filter
        plants = get_active_plants()
        plant_options = ["All Plants"] + [f"{p['name']} (#{p['id']})" for p in plants]
        self.plant_filter = ctk.StringVar(value="All Plants")
        ctk.CTkOptionMenu(inner_top, values=plant_options, variable=self.plant_filter,
                          width=180, command=lambda _: self._refresh_events()).pack(side="right", padx=5)

        # Events list
        self.events_scroll = ctk.CTkScrollableFrame(
            self.parent, fg_color="transparent",
            scrollbar_button_color=self.colors["bg_tertiary"],
        )
        self.events_scroll.pack(fill="both", expand=True)
        self._refresh_events()

    def _refresh_events(self):
        for w in self.events_scroll.winfo_children():
            w.destroy()

        plant_filter = self.plant_filter.get()
        plant_id = None
        if plant_filter != "All Plants":
            plant_id = extract_id_from_option(plant_filter)

        if plant_id:
            events = get_plant_events(plant_id, limit=200)
            # Add plant_name manually
            for ev in events:
                ev["plant_name"] = plant_filter.split(" (")[0]
        else:
            events = get_recent_events(200)

        if not events:
            empty = ctk.CTkFrame(self.events_scroll, fg_color="transparent")
            empty.pack(fill="x", pady=40)
            ctk.CTkLabel(empty, text="No events recorded yet.",
                        text_color=self.colors["fg_muted"],
                        font=ctk.CTkFont(size=14)).pack()
            ctk.CTkLabel(empty, text='Click "➕ New Entry" to add your first journal entry.',
                        text_color=self.colors["fg_muted"],
                        font=ctk.CTkFont(size=12)).pack(pady=(5, 0))
            return

        current_date = ""
        for ev in events:
            ev_date = ev.get("event_date", "")[:10]

            if ev_date != current_date:
                current_date = ev_date
                ctk.CTkLabel(self.events_scroll, text=f"📅 {current_date}",
                            font=ctk.CTkFont(size=14, weight="bold"),
                            text_color=self.colors["accent"]).pack(anchor="w", padx=25, pady=(15, 5))

            self._event_card(self.events_scroll, ev)

    def _event_card(self, parent, ev):
        card = ctk.CTkFrame(parent, fg_color=self.colors["bg_card"], corner_radius=10)
        card.pack(fill="x", padx=25, pady=3)

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=15, pady=10)

        # Type icon
        type_icons = {
            "Watering": "💧", "Feeding": "🧪", "Training (LST)": "🌿",
            "Training (Topping)": "✂️", "Pruning": "✂️", "Transplant": "🪴",
            "Stage Change": "⏭️", "Photo": "📸", "Observation": "👁️",
            "pH Reading": "⚗️", "EC/PPM Reading": "📊", "Pest Treatment": "🐛",
            "Issue Detected": "⚠️", "Harvest": "🌾", "Clone Taken": "🧬",
            "Pollination": "🔬",
        }
        icon = type_icons.get(ev.get("event_type", ""), "📝")
        etype = ev.get("event_type", "Unknown")
        pname = ev.get("plant_name", "")
        time_str = ev.get("event_date", "")[11:16] if len(ev.get("event_date", "")) > 11 else ""

        top_row = ctk.CTkFrame(inner, fg_color="transparent")
        top_row.pack(fill="x")

        ctk.CTkLabel(top_row, text=f"{icon} {etype}",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=self.colors["fg_primary"]).pack(side="left")

        # Delete button
        ev_id = ev.get("id")
        if ev_id:
            ctk.CTkButton(
                top_row, text="🗑️", width=28, height=28,
                fg_color="transparent", hover_color=self.colors["error"],
                text_color=self.colors["fg_muted"],
                font=ctk.CTkFont(size=12),
                command=lambda eid=ev_id, ename=etype, epname=pname: self._delete_event(eid, ename, epname),
            ).pack(side="right")

        if pname:
            ctk.CTkLabel(top_row, text=pname,
                         font=ctk.CTkFont(size=11),
                         text_color=self.colors["accent"]).pack(side="right", padx=(0, 10))

        if time_str:
            ctk.CTkLabel(top_row, text=time_str,
                         font=ctk.CTkFont(size=10),
                         text_color=self.colors["fg_muted"]).pack(side="right")

        # Metrics row
        metrics = []
        if ev.get("ph"): metrics.append(f"pH {ev['ph']}")
        if ev.get("ec"): metrics.append(f"EC {ev['ec']}")
        if ev.get("temp"): metrics.append(f"{ev['temp']}°C")
        if ev.get("humidity"): metrics.append(f"{ev['humidity']}% RH")
        if ev.get("vpd"): metrics.append(f"VPD {ev['vpd']}")
        if ev.get("water_ml"): metrics.append(f"{ev['water_ml']}ml")

        if metrics:
            ctk.CTkLabel(inner, text=" • ".join(metrics),
                        font=ctk.CTkFont(size=11),
                        text_color=self.colors["info"]).pack(anchor="w", pady=(3, 0))

        if ev.get("nutrient_mix"):
            ctk.CTkLabel(inner, text=f"🧪 {ev['nutrient_mix']}",
                        font=ctk.CTkFont(size=11),
                        text_color=self.colors["fg_secondary"]).pack(anchor="w", pady=(2, 0))

        if ev.get("notes"):
            ctk.CTkLabel(inner, text=ev["notes"],
                        font=ctk.CTkFont(size=11),
                        text_color=self.colors["fg_secondary"],
                        wraplength=700, justify="left").pack(anchor="w", pady=(3, 0))

    def _add_event_dialog(self):
        plants = get_active_plants()
        if not plants:
            dialog = ctk.CTkToplevel(self.parent)
            dialog.title("No Plants")
            dialog.geometry("350x120")
            dialog.transient(self.parent)
            dialog.after(50, lambda: dialog.grab_set())
            ctk.CTkLabel(dialog, text="No active plants found.",
                        font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(20, 5))
            ctk.CTkLabel(dialog, text="Add a plant in the Plants tab first.",
                        font=ctk.CTkFont(size=12)).pack()
            ctk.CTkButton(dialog, text="OK", width=80, command=dialog.destroy).pack(pady=10)
            return

        dialog = ctk.CTkToplevel(self.parent)
        dialog.title("New Journal Entry")
        dialog.geometry("520x620")
        dialog.transient(self.parent)
        dialog.after(50, lambda: dialog.grab_set())

        scroll = ctk.CTkScrollableFrame(dialog, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(scroll, text="📝 New Journal Entry",
                    font=ctk.CTkFont(size=18, weight="bold"),
                    text_color=self.colors["fg_primary"]).pack(pady=(0, 15))

        fields = {}

        # Plant selector
        ctk.CTkLabel(scroll, text="Plant *", font=ctk.CTkFont(size=12, weight="bold"),
                    text_color=self.colors["fg_primary"]).pack(anchor="w", pady=(5, 2))
        plant_options = [f"{p['name']} (#{p['id']})" for p in plants]
        plant_var = ctk.StringVar(value=plant_options[0])
        ctk.CTkOptionMenu(scroll, values=plant_options, variable=plant_var, width=460).pack(fill="x")
        fields["plant"] = plant_var

        # Event type
        ctk.CTkLabel(scroll, text="Event Type *", font=ctk.CTkFont(size=12, weight="bold"),
                    text_color=self.colors["fg_primary"]).pack(anchor="w", pady=(10, 2))
        etype_var = ctk.StringVar(value="Watering")
        ctk.CTkOptionMenu(scroll, values=EVENT_TYPES, variable=etype_var, width=460).pack(fill="x")
        fields["type"] = etype_var

        # Metric fields
        def add_metric(label, default=""):
            ctk.CTkLabel(scroll, text=label, font=ctk.CTkFont(size=12),
                        text_color=self.colors["fg_secondary"]).pack(anchor="w", pady=(8, 2))
            var = ctk.StringVar(value=default)
            ctk.CTkEntry(scroll, textvariable=var, width=460,
                        fg_color=self.colors["bg_input"]).pack(fill="x")
            fields[label] = var

        add_metric("pH")
        add_metric("EC (mS/cm)")
        add_metric("Temperature (°C)")
        add_metric("Humidity (%)")
        add_metric("Water Amount (ml)")
        add_metric("Nutrient Mix")

        # Notes
        ctk.CTkLabel(scroll, text="Notes", font=ctk.CTkFont(size=12),
                    text_color=self.colors["fg_secondary"]).pack(anchor="w", pady=(8, 2))
        notes_box = ctk.CTkTextbox(scroll, height=80, width=460,
                                   fg_color=self.colors["bg_input"])
        notes_box.pack(fill="x")

        # Error area
        error_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        error_frame.pack(fill="x", pady=(5, 0))

        def save():
            # Clear previous errors
            for w in error_frame.winfo_children():
                w.destroy()

            # Validate plant selection
            plant_id = extract_id_from_option(fields["plant"].get())
            if not plant_id:
                show_validation_error(error_frame, "Please select a plant.", self.colors)
                return

            def opt_float(val):
                try:
                    return float(val) if val and val.strip() else None
                except (ValueError, TypeError):
                    return None

            ph = opt_float(fields["pH"].get())
            ec = opt_float(fields["EC (mS/cm)"].get())
            temp = opt_float(fields["Temperature (°C)"].get())
            rh = opt_float(fields["Humidity (%)"].get())
            water = opt_float(fields["Water Amount (ml)"].get())

            # Calculate VPD if we have temp and humidity
            vpd_val = None
            if temp and rh:
                from utils.vpd_calculator import calculate_vpd
                vpd_val = calculate_vpd(temp, rh)

            # Find plant's environment_id
            selected_plant = None
            for p in plants:
                if p["id"] == plant_id:
                    selected_plant = p
                    break

            data = {
                "plant_id": plant_id,
                "environment_id": selected_plant.get("environment_id") if selected_plant else None,
                "event_type": fields["type"].get(),
                "event_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "title": fields["type"].get(),
                "notes": notes_box.get("1.0", "end-1c"),
                "ph": ph,
                "ec": ec,
                "temp": temp,
                "humidity": rh,
                "vpd": vpd_val,
                "water_ml": water,
                "nutrient_mix": fields["Nutrient Mix"].get(),
            }
            insert_row("events", data)
            dialog.destroy()
            self._refresh_events()

        ctk.CTkButton(
            scroll, text="💾 Save Entry", height=40,
            font=ctk.CTkFont(size=14, weight="bold"), corner_radius=8,
            fg_color=self.colors["accent"],
            hover_color=self.colors["accent_hover"],
            command=save,
        ).pack(fill="x", pady=(15, 5))

    def _delete_event(self, event_id, event_type, plant_name):
        confirm = ctk.CTkToplevel(self.parent)
        confirm.title("Delete Entry")
        confirm.geometry("400x160")
        confirm.transient(self.parent)
        confirm.after(50, lambda: confirm.grab_set())

        label = f"{event_type}"
        if plant_name:
            label += f" — {plant_name}"

        ctk.CTkLabel(
            confirm, text="Delete this journal entry?",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors["fg_primary"],
        ).pack(pady=(20, 5))
        ctk.CTkLabel(
            confirm, text=label,
            font=ctk.CTkFont(size=12),
            text_color=self.colors["fg_muted"],
        ).pack(pady=5)

        bf = ctk.CTkFrame(confirm, fg_color="transparent")
        bf.pack(pady=15)

        ctk.CTkButton(
            bf, text="Cancel", width=120,
            fg_color=self.colors["bg_tertiary"],
            command=confirm.destroy,
        ).pack(side="left", padx=10)

        def do_delete():
            delete_row("events", event_id)
            confirm.destroy()
            self._refresh_events()

        ctk.CTkButton(
            bf, text="🗑️ Delete", width=120,
            fg_color=self.colors["error"],
            hover_color="#d32f2f",
            command=do_delete,
        ).pack(side="left", padx=10)

    def _search(self):
        query = self.search_var.get().strip()
        if not query:
            self._refresh_events()
            return

        for w in self.events_scroll.winfo_children():
            w.destroy()

        results = search_events(query)
        if not results:
            ctk.CTkLabel(self.events_scroll, text=f'No results for "{query}"',
                        text_color=self.colors["fg_muted"]).pack(pady=40)
            return

        ctk.CTkLabel(self.events_scroll, text=f'🔍 {len(results)} results for "{query}"',
                    font=ctk.CTkFont(size=14, weight="bold"),
                    text_color=self.colors["fg_primary"]).pack(anchor="w", padx=25, pady=(15, 10))

        for ev in results:
            self._event_card(self.events_scroll, ev)
