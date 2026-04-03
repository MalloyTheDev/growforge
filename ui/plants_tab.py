# FILE: growforge/ui/plants_tab.py
"""
GrowForge — Plants management tab.
Add/edit plants, track stages, view details with stage guidance.
"""

import customtkinter as ctk
from datetime import datetime
from database import get_active_plants, get_all, insert_row, update_row
from config import STAGES, PLANT_TYPES, GENETICS_TYPES, MEDIUMS, STAGE_COLORS
from knowledge_base import STAGE_GUIDE
from ui.helpers import (
    validate_not_empty, validate_date, safe_float, show_validation_error,
)


class PlantsTab:
    """Plants management with add/edit/view and stage guidance."""

    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.colors = app.colors
        self._build()

    def _build(self):
        scroll = ctk.CTkScrollableFrame(
            self.parent, fg_color="transparent",
            scrollbar_button_color=self.colors["bg_tertiary"],
        )
        scroll.pack(fill="both", expand=True)

        # Header
        header = ctk.CTkFrame(scroll, fg_color="transparent")
        header.pack(fill="x", padx=25, pady=(20, 10))

        ctk.CTkLabel(
            header, text="🌱 Plant Manager",
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color=self.colors["fg_primary"],
        ).pack(side="left")

        ctk.CTkButton(
            header, text="➕ Add Plant", width=130, height=36,
            font=ctk.CTkFont(size=13), corner_radius=8,
            fg_color=self.colors["accent"],
            hover_color=self.colors["accent_hover"],
            command=self._add_plant_dialog,
        ).pack(side="right")

        # Plant list
        plants = get_active_plants()
        if not plants:
            ctk.CTkLabel(
                scroll, text="No plants yet! Click 'Add Plant' to start.",
                font=ctk.CTkFont(size=14),
                text_color=self.colors["fg_muted"],
            ).pack(pady=40)
            return

        for plant in plants:
            self._plant_card(scroll, plant)

    def _plant_card(self, parent, plant):
        card = ctk.CTkFrame(parent, fg_color=self.colors["bg_card"], corner_radius=12)
        card.pack(fill="x", padx=25, pady=5)

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=18, pady=14)

        # Top row: name + stage badge
        top = ctk.CTkFrame(inner, fg_color="transparent")
        top.pack(fill="x")

        name = plant.get("name", "Unknown")
        is_mother = " 👑" if plant.get("is_mother") else ""

        ctk.CTkLabel(
            top, text=f"{name}{is_mother}",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors["fg_primary"],
        ).pack(side="left")

        stage = plant.get("stage", "?")

        ctk.CTkLabel(
            top, text=f" {stage} ",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#fff",
            fg_color=STAGE_COLORS.get(stage, "#888"),
            corner_radius=4,
        ).pack(side="right")

        # Detail row
        details = []
        if plant.get("strain_name"):
            details.append(plant["strain_name"])
        # Show strain type from strains table if available
        if plant.get("strain_id"):
            from database import get_row
            strain = get_row("strains", plant["strain_id"])
            if strain and strain.get("strain_type"):
                details.append(strain["strain_type"])
        details.append(plant.get("plant_type", "Photo"))
        if plant.get("start_date"):
            try:
                start = datetime.strptime(plant["start_date"], "%Y-%m-%d")
                days = (datetime.now() - start).days
                details.append(f"Day {days}")
            except ValueError:
                pass
        if plant.get("medium"):
            details.append(plant["medium"])

        ctk.CTkLabel(
            inner, text=" • ".join([d for d in details if d]),
            font=ctk.CTkFont(size=12),
            text_color=self.colors["fg_secondary"],
        ).pack(anchor="w", pady=(3, 0))

        # Stage guidance bar
        if stage in STAGE_GUIDE:
            guide = STAGE_GUIDE[stage]
            guide_parts = []
            if guide.get("temp_range"):
                guide_parts.append(f"🌡️ {guide['temp_range'][0]}-{guide['temp_range'][1]}°C")
            if guide.get("rh_range"):
                guide_parts.append(f"💧 {guide['rh_range'][0]}-{guide['rh_range'][1]}%")
            if guide.get("vpd_target"):
                guide_parts.append(f"📊 VPD {guide['vpd_target'][0]}-{guide['vpd_target'][1]}")

            if guide_parts:
                ctk.CTkLabel(
                    inner, text="  ".join(guide_parts),
                    font=ctk.CTkFont(size=11),
                    text_color=self.colors["fg_muted"],
                ).pack(anchor="w", pady=(2, 0))

        # Buttons row
        btns = ctk.CTkFrame(inner, fg_color="transparent")
        btns.pack(fill="x", pady=(8, 0))

        ctk.CTkButton(
            btns, text="📝 Log Event", width=100, height=30,
            font=ctk.CTkFont(size=11), corner_radius=6,
            fg_color=self.colors["accent_dark"],
            hover_color=self.colors["accent"],
            command=lambda p=plant: self._log_event_dialog(p),
        ).pack(side="left", padx=(0, 5))

        ctk.CTkButton(
            btns, text="⏭️ Next Stage", width=100, height=30,
            font=ctk.CTkFont(size=11), corner_radius=6,
            fg_color=self.colors["bg_tertiary"],
            hover_color=self.colors["highlight"],
            command=lambda p=plant: self._advance_stage(p),
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            btns, text="✏️ Edit", width=70, height=30,
            font=ctk.CTkFont(size=11), corner_radius=6,
            fg_color=self.colors["bg_tertiary"],
            hover_color=self.colors["highlight"],
            command=lambda p=plant: self._edit_plant_dialog(p),
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            btns, text="🗑️", width=40, height=30,
            font=ctk.CTkFont(size=11), corner_radius=6,
            fg_color=self.colors["bg_tertiary"],
            hover_color=self.colors["error"],
            command=lambda p=plant: self._delete_plant(p),
        ).pack(side="right")

    def _add_plant_dialog(self):
        dialog = ctk.CTkToplevel(self.parent)
        dialog.title("Add New Plant")
        dialog.geometry("500x650")
        dialog.transient(self.parent)
        dialog.after(50, lambda: dialog.grab_set())

        scroll = ctk.CTkScrollableFrame(dialog, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(scroll, text="Add New Plant", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(0, 15))

        fields = {}

        def add_field(label, default="", options=None):
            ctk.CTkLabel(scroll, text=label, font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(8, 2))
            if options:
                var = ctk.StringVar(value=options[0] if default == "" else default)
                w = ctk.CTkOptionMenu(scroll, values=options, variable=var, width=400)
                w.pack(fill="x")
                fields[label] = var
            else:
                var = ctk.StringVar(value=default)
                w = ctk.CTkEntry(scroll, textvariable=var, width=400)
                w.pack(fill="x")
                fields[label] = var

        # Get strains and environments for dropdowns
        strains = get_all("strains")
        strain_names = ["(None)"] + [s["name"] for s in strains]
        envs = get_all("environments")
        env_names = ["(None)"] + [f"{e['name']} (#{e['id']})" for e in envs]

        add_field("Plant Name", f"Plant #{len(get_active_plants()) + 1}")
        add_field("Strain", "", strain_names)
        add_field("Plant Type", "Photoperiod", PLANT_TYPES)
        add_field("Genetics Type", "Feminized", GENETICS_TYPES)
        add_field("Starting Stage", "Germination", STAGES)
        add_field("Environment", "", env_names)
        add_field("Medium", "", MEDIUMS)
        add_field("Pot Size", "")
        add_field("Start Date (YYYY-MM-DD)", datetime.now().strftime("%Y-%m-%d"))

        # Notes
        ctk.CTkLabel(scroll, text="Notes", font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(8, 2))
        notes_box = ctk.CTkTextbox(scroll, height=80, width=400)
        notes_box.pack(fill="x")

        # Is mother checkbox
        is_mother_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(scroll, text="Designate as Mother Plant 👑", variable=is_mother_var).pack(anchor="w", pady=8)

        # Error label placeholder
        self._add_err = None

        def save():
            # Clear previous error
            if self._add_err:
                self._add_err.destroy()
                self._add_err = None

            plant_name = fields["Plant Name"].get().strip()
            err = validate_not_empty(plant_name, "Plant Name")
            if not err:
                err = validate_date(fields["Start Date (YYYY-MM-DD)"].get(), "Start Date")
            if err:
                self._add_err = show_validation_error(scroll, err, self.colors)
                return

            strain_val = fields["Strain"].get()
            strain_id = None
            strain_name = ""
            if strain_val != "(None)":
                strain_name = strain_val
                for s in strains:
                    if s["name"] == strain_val:
                        strain_id = s["id"]
                        break

            env_val = fields["Environment"].get()
            env_id = None
            if env_val != "(None)":
                for e in envs:
                    if f"{e['name']} (#{e['id']})" == env_val:
                        env_id = e["id"]
                        break

            stage = fields["Starting Stage"].get()
            data = {
                "name": plant_name,
                "strain_id": strain_id,
                "strain_name": strain_name,
                "plant_type": fields["Plant Type"].get(),
                "genetics_type": fields["Genetics Type"].get(),
                "stage": stage,
                "environment_id": env_id,
                "medium": fields["Medium"].get(),
                "pot_size": fields["Pot Size"].get(),
                "start_date": fields["Start Date (YYYY-MM-DD)"].get(),
                "notes": notes_box.get("1.0", "end-1c"),
                "is_mother": 1 if is_mother_var.get() else 0,
                "is_active": 1,
            }

            # Set stage dates
            if stage == "Germination":
                data["germ_date"] = data["start_date"]
            elif stage == "Seedling":
                data["germ_date"] = data["start_date"]
            elif stage == "Vegetative":
                data["veg_date"] = data["start_date"]
            elif stage == "Flowering":
                data["flower_date"] = data["start_date"]

            new_plant_id = insert_row("plants", data)

            # Log stage change event
            insert_row("events", {
                "plant_id": new_plant_id,
                "event_type": "Stage Change",
                "event_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "title": f"Plant created in {stage}",
                "notes": f"New plant '{data['name']}' started in {stage} stage.",
            })

            dialog.destroy()
            self.app.refresh_current_tab()

        ctk.CTkButton(
            scroll, text="💾 Save Plant", height=40,
            font=ctk.CTkFont(size=14), corner_radius=8,
            fg_color=self.colors["accent"],
            command=save,
        ).pack(fill="x", pady=(15, 5))

    def _edit_plant_dialog(self, plant):
        dialog = ctk.CTkToplevel(self.parent)
        dialog.title(f"Edit: {plant['name']}")
        dialog.geometry("500x600")
        dialog.transient(self.parent)
        dialog.after(50, lambda: dialog.grab_set())

        scroll = ctk.CTkScrollableFrame(dialog, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(scroll, text=f"Edit {plant['name']}", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(0, 15))

        fields = {}

        def add_field(label, default="", options=None):
            ctk.CTkLabel(scroll, text=label, font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(8, 2))
            if options:
                var = ctk.StringVar(value=default)
                w = ctk.CTkOptionMenu(scroll, values=options, variable=var, width=400)
                w.pack(fill="x")
                fields[label] = var
            else:
                var = ctk.StringVar(value=default)
                w = ctk.CTkEntry(scroll, textvariable=var, width=400)
                w.pack(fill="x")
                fields[label] = var

        add_field("Plant Name", plant.get("name", ""))
        add_field("Strain Name", plant.get("strain_name", ""))
        add_field("Plant Type", plant.get("plant_type", "Photoperiod"), PLANT_TYPES)
        add_field("Stage", plant.get("stage", "Germination"), STAGES)
        add_field("Medium", plant.get("medium", ""), MEDIUMS)
        add_field("Pot Size", plant.get("pot_size", ""))

        # Yield (for harvested)
        add_field("Yield (grams)", str(plant.get("yield_grams", 0)))

        # Notes
        ctk.CTkLabel(scroll, text="Notes", font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(8, 2))
        notes_box = ctk.CTkTextbox(scroll, height=80, width=400)
        notes_box.pack(fill="x")
        notes_box.insert("1.0", plant.get("notes", ""))

        is_mother_var = ctk.BooleanVar(value=bool(plant.get("is_mother")))
        ctk.CTkCheckBox(scroll, text="Mother Plant 👑", variable=is_mother_var).pack(anchor="w", pady=8)

        self._edit_err = None

        def save():
            if self._edit_err:
                self._edit_err.destroy()
                self._edit_err = None

            name = fields["Plant Name"].get().strip()
            err = validate_not_empty(name, "Plant Name")
            if err:
                self._edit_err = show_validation_error(scroll, err, self.colors)
                return

            data = {
                "name": name,
                "strain_name": fields["Strain Name"].get(),
                "plant_type": fields["Plant Type"].get(),
                "stage": fields["Stage"].get(),
                "medium": fields["Medium"].get(),
                "pot_size": fields["Pot Size"].get(),
                "notes": notes_box.get("1.0", "end-1c"),
                "is_mother": 1 if is_mother_var.get() else 0,
                "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            data["yield_grams"] = safe_float(fields["Yield (grams)"].get(), 0.0)

            # Update stage dates
            new_stage = fields["Stage"].get()
            old_stage = plant.get("stage", "")
            if new_stage != old_stage:
                now = datetime.now().strftime("%Y-%m-%d")
                if new_stage == "Vegetative":
                    data["veg_date"] = now
                elif new_stage == "Flowering":
                    data["flower_date"] = now
                elif new_stage == "Harvested":
                    data["harvest_date"] = now
                    data["is_active"] = 0

            update_row("plants", plant["id"], data)
            dialog.destroy()
            self.app.refresh_current_tab()

        ctk.CTkButton(
            scroll, text="💾 Save Changes", height=40,
            font=ctk.CTkFont(size=14), corner_radius=8,
            fg_color=self.colors["accent"],
            command=save,
        ).pack(fill="x", pady=(15, 5))

    def _advance_stage(self, plant):
        current_idx = STAGES.index(plant["stage"]) if plant["stage"] in STAGES else 0
        if current_idx >= len(STAGES) - 1:
            # Already at final stage
            info = ctk.CTkToplevel(self.parent)
            info.title("Stage Complete")
            info.geometry("350x120")
            info.transient(self.parent)
            info.after(50, lambda: info.grab_set())
            ctk.CTkLabel(info, text=f"'{plant['name']}' is already at {plant['stage']}.",
                        font=ctk.CTkFont(size=14),
                        text_color=self.colors["fg_primary"]).pack(pady=(25, 5))
            ctk.CTkButton(info, text="OK", width=80,
                         fg_color=self.colors["accent"],
                         command=info.destroy).pack(pady=10)
            return

        next_stage = STAGES[current_idx + 1]

        # Confirmation dialog
        confirm = ctk.CTkToplevel(self.parent)
        confirm.title("Advance Stage")
        confirm.geometry("420x180")
        confirm.transient(self.parent)
        confirm.after(50, lambda: confirm.grab_set())

        ctk.CTkLabel(confirm, text=f"Advance '{plant['name']}'?",
                    font=ctk.CTkFont(size=16, weight="bold"),
                    text_color=self.colors["fg_primary"]).pack(pady=(20, 5))
        ctk.CTkLabel(confirm,
                    text=f"{plant['stage']}  →  {next_stage}",
                    font=ctk.CTkFont(size=14),
                    text_color=self.colors["accent"]).pack(pady=5)

        if next_stage == "Harvested":
            ctk.CTkLabel(confirm, text="Plant will be marked inactive after harvest.",
                        font=ctk.CTkFont(size=11),
                        text_color=self.colors["warning"]).pack()

        bf = ctk.CTkFrame(confirm, fg_color="transparent")
        bf.pack(pady=12)

        ctk.CTkButton(bf, text="Cancel", width=120,
                     fg_color=self.colors["bg_tertiary"],
                     command=confirm.destroy).pack(side="left", padx=10)

        def do_advance():
            now = datetime.now().strftime("%Y-%m-%d")
            now_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            data = {"stage": next_stage, "updated_at": now_ts}

            if next_stage == "Vegetative":
                data["veg_date"] = now
            elif next_stage == "Flowering":
                data["flower_date"] = now
            elif next_stage == "Harvested":
                data["harvest_date"] = now
                data["is_active"] = 0

            update_row("plants", plant["id"], data)

            insert_row("events", {
                "plant_id": plant["id"],
                "event_type": "Stage Change",
                "event_date": now_ts,
                "title": f"Advanced to {next_stage}",
                "notes": f"Stage changed from {plant['stage']} to {next_stage}.",
            })

            # Auto-create stage-appropriate reminders
            self._create_stage_reminders(plant["id"], plant.get("name", "Plant"), next_stage)

            confirm.destroy()
            self.app.refresh_current_tab()

        ctk.CTkButton(bf, text=f"⏭️ Advance to {next_stage}", width=180,
                     fg_color=self.colors["accent"],
                     hover_color=self.colors["accent_hover"],
                     command=do_advance).pack(side="left", padx=10)

    def _create_stage_reminders(self, plant_id, plant_name, stage):
        """Auto-create reminders based on the new stage."""
        from datetime import timedelta

        now = datetime.now()
        reminders = []

        if stage == "Seedling":
            reminders.append(("Watering", 1, f"Check {plant_name} — seedlings dry out fast"))
            reminders.append(("Observation", 2, f"Check {plant_name} for first true leaves"))
        elif stage == "Vegetative":
            reminders.append(("Feeding", 3, f"Start veg nutrients for {plant_name}"))
            reminders.append(("Watering", 2, f"Water {plant_name} (recurring veg schedule)"))
            reminders.append(("Training (LST)", 7, f"Consider LST/topping for {plant_name}"))
        elif stage == "Flowering":
            reminders.append(("Feeding", 3, f"Switch {plant_name} to bloom nutrients"))
            reminders.append(("Light Change", 0, f"Confirm 12/12 light for {plant_name}"))
            reminders.append(("Observation", 14, f"Check {plant_name} for preflowers"))
        elif stage == "Flushing":
            reminders.append(("Watering", 1, f"Flush {plant_name} — plain water only"))
            reminders.append(("Observation", 7, f"Check trichomes on {plant_name}"))
        elif stage == "Drying":
            reminders.append(("Observation", 5, f"Check {plant_name} drying progress (stem snap test)"))
        elif stage == "Curing":
            reminders.append(("Observation", 1, f"Burp jars for {plant_name}"))
            reminders.append(("Observation", 14, f"Check {plant_name} cure quality"))

        for rtype, days_ahead, message in reminders:
            due = (now + timedelta(days=days_ahead)).strftime("%Y-%m-%d %H:%M:%S")
            insert_row("reminders", {
                "plant_id": plant_id,
                "reminder_type": rtype,
                "due_date": due,
                "message": message,
                "is_recurring": 1 if rtype in ("Watering", "Feeding") else 0,
                "recurrence_days": days_ahead if rtype in ("Watering", "Feeding") else 0,
            })

    def _log_event_dialog(self, plant):
        from config import EVENT_TYPES

        dialog = ctk.CTkToplevel(self.parent)
        dialog.title(f"Log Event: {plant['name']}")
        dialog.geometry("500x580")
        dialog.transient(self.parent)
        dialog.after(50, lambda: dialog.grab_set())

        scroll = ctk.CTkScrollableFrame(dialog, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(scroll, text=f"📝 Log Event for {plant['name']}", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(0, 15))

        fields = {}

        ctk.CTkLabel(scroll, text="Event Type", font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(5, 2))
        etype_var = ctk.StringVar(value="Watering")
        ctk.CTkOptionMenu(scroll, values=EVENT_TYPES, variable=etype_var, width=400).pack(fill="x")
        fields["type"] = etype_var

        def add_metric(label, default=""):
            ctk.CTkLabel(scroll, text=label, font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(5, 2))
            var = ctk.StringVar(value=default)
            ctk.CTkEntry(scroll, textvariable=var, width=400).pack(fill="x")
            fields[label] = var

        add_metric("pH")
        add_metric("EC (mS/cm)")
        add_metric("Temperature (°C)")
        add_metric("Humidity (%)")
        add_metric("Water Amount (ml)")
        add_metric("Nutrient Mix")

        ctk.CTkLabel(scroll, text="Notes", font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(5, 2))
        notes_box = ctk.CTkTextbox(scroll, height=80, width=400)
        notes_box.pack(fill="x")

        def save():
            def opt_float(val):
                """Parse float, return None if empty/invalid (for optional fields)."""
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

            data = {
                "plant_id": plant["id"],
                "environment_id": plant.get("environment_id"),
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
            self.app.refresh_current_tab()

        ctk.CTkButton(
            scroll, text="💾 Save Event", height=40,
            font=ctk.CTkFont(size=14), corner_radius=8,
            fg_color=self.colors["accent"],
            command=save,
        ).pack(fill="x", pady=(15, 5))

    def _delete_plant(self, plant):
        confirm = ctk.CTkToplevel(self.parent)
        confirm.title("Confirm Delete")
        confirm.geometry("400x150")
        confirm.transient(self.parent)
        confirm.after(50, lambda: confirm.grab_set())

        ctk.CTkLabel(
            confirm, text=f"Delete '{plant['name']}'?",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(pady=(20, 5))
        ctk.CTkLabel(
            confirm, text="This will deactivate the plant. Events will be kept.",
            font=ctk.CTkFont(size=12),
        ).pack(pady=5)

        bf = ctk.CTkFrame(confirm, fg_color="transparent")
        bf.pack(pady=15)

        ctk.CTkButton(
            bf, text="Cancel", width=120,
            fg_color=self.colors["bg_tertiary"],
            command=confirm.destroy,
        ).pack(side="left", padx=10)

        def do_delete():
            update_row("plants", plant["id"], {"is_active": 0})
            confirm.destroy()
            self.app.refresh_current_tab()

        ctk.CTkButton(
            bf, text="🗑️ Delete", width=120,
            fg_color=self.colors["error"],
            command=do_delete,
        ).pack(side="left", padx=10)
