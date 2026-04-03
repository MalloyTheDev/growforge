# FILE: growforge/ui/environments_tab.py
"""
GrowForge — Environments management tab (tents, rooms, grow spaces).
"""

import customtkinter as ctk
from database import get_all, insert_row, update_row, delete_row, get_plants_by_environment
from config import MEDIUMS, LIGHT_TYPES
from ui.helpers import safe_int, validate_not_empty, show_validation_error


class EnvironmentsTab:
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

        ctk.CTkLabel(header, text="🏠 Environments",
                     font=ctk.CTkFont(size=26, weight="bold"),
                     text_color=self.colors["fg_primary"]).pack(side="left")

        ctk.CTkButton(header, text="➕ Add Environment", width=160, height=36,
                      fg_color=self.colors["accent"], hover_color=self.colors["accent_hover"],
                      command=self._add_env_dialog).pack(side="right")

        envs = get_all("environments")
        if not envs:
            ctk.CTkLabel(scroll, text="No environments yet. Add your first tent or room!",
                        text_color=self.colors["fg_muted"], font=ctk.CTkFont(size=14)).pack(pady=40)
            return

        for env in envs:
            self._env_card(scroll, env)

    def _env_card(self, parent, env):
        card = ctk.CTkFrame(parent, fg_color=self.colors["bg_card"], corner_radius=12)
        card.pack(fill="x", padx=25, pady=5)
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=18, pady=14)

        top = ctk.CTkFrame(inner, fg_color="transparent")
        top.pack(fill="x")

        ctk.CTkLabel(top, text=f"🏠 {env.get('name', '?')}",
                     font=ctk.CTkFont(size=16, weight="bold"),
                     text_color=self.colors["fg_primary"]).pack(side="left")

        ctk.CTkLabel(top, text=env.get("env_type", ""),
                     font=ctk.CTkFont(size=11),
                     text_color=self.colors["fg_muted"]).pack(side="right")

        details = []
        if env.get("light_type"): details.append(f"💡 {env['light_type']}")
        if env.get("light_wattage"): details.append(f"{env['light_wattage']}W")
        if env.get("light_schedule"): details.append(f"⏰ {env['light_schedule']}")
        if env.get("medium"): details.append(f"🪴 {env['medium']}")
        if env.get("tent_size"): details.append(f"📐 {env['tent_size']}")

        if details:
            ctk.CTkLabel(inner, text=" • ".join(details),
                        font=ctk.CTkFont(size=12),
                        text_color=self.colors["fg_secondary"]).pack(anchor="w", pady=(4, 0))

        # Plants in this environment
        plants = get_plants_by_environment(env["id"])
        if plants:
            pnames = ", ".join([p["name"] for p in plants[:5]])
            ctk.CTkLabel(inner, text=f"🌱 Plants: {pnames}" + (" ..." if len(plants) > 5 else ""),
                        font=ctk.CTkFont(size=11),
                        text_color=self.colors["fg_muted"]).pack(anchor="w", pady=(3, 0))

        btns = ctk.CTkFrame(inner, fg_color="transparent")
        btns.pack(fill="x", pady=(8, 0))

        ctk.CTkButton(btns, text="✏️ Edit", width=70, height=28,
                      fg_color=self.colors["bg_tertiary"], hover_color=self.colors["highlight"],
                      font=ctk.CTkFont(size=11),
                      command=lambda e=env: self._edit_env_dialog(e)).pack(side="left", padx=(0, 5))

        ctk.CTkButton(btns, text="🗑️", width=40, height=28,
                      fg_color=self.colors["bg_tertiary"], hover_color=self.colors["error"],
                      font=ctk.CTkFont(size=11),
                      command=lambda e=env: self._delete_env(e)).pack(side="right")

    def _add_env_dialog(self):
        dialog = ctk.CTkToplevel(self.parent)
        dialog.title("Add Environment")
        dialog.geometry("480x550")
        dialog.transient(self.parent)
        dialog.after(50, lambda: dialog.grab_set())

        scroll = ctk.CTkScrollableFrame(dialog, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(scroll, text="Add Environment", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(0, 15))

        fields = {}
        env_types = ["Indoor Tent", "Indoor Room", "Greenhouse", "Outdoor", "Closet", "Cabinet"]

        def add_field(label, default="", options=None):
            ctk.CTkLabel(scroll, text=label, font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(8, 2))
            if options:
                var = ctk.StringVar(value=default or options[0])
                ctk.CTkOptionMenu(scroll, values=options, variable=var, width=380).pack(fill="x")
                fields[label] = var
            else:
                var = ctk.StringVar(value=default)
                ctk.CTkEntry(scroll, textvariable=var, width=380).pack(fill="x")
                fields[label] = var

        add_field("Name", "")
        add_field("Type", "Indoor Tent", env_types)
        add_field("Medium", "Soil (Organic)", MEDIUMS)
        add_field("Light Type", "LED (Full Spectrum)", LIGHT_TYPES)
        add_field("Light Wattage", "")
        add_field("Light Schedule", "18/6")
        add_field("Tent/Room Size", "")

        ctk.CTkLabel(scroll, text="Notes", font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(8, 2))
        notes = ctk.CTkTextbox(scroll, height=60, width=380)
        notes.pack(fill="x")

        self._add_env_err = None

        def save():
            if self._add_env_err:
                self._add_env_err.destroy()
                self._add_env_err = None

            name = fields["Name"].get().strip()
            err = validate_not_empty(name, "Name")
            if err:
                self._add_env_err = show_validation_error(scroll, err, self.colors)
                return

            data = {
                "name": name,
                "env_type": fields["Type"].get(),
                "medium": fields["Medium"].get(),
                "light_type": fields["Light Type"].get(),
                "light_wattage": safe_int(fields["Light Wattage"].get(), 0),
                "light_schedule": fields["Light Schedule"].get(),
                "tent_size": fields["Tent/Room Size"].get(),
                "notes": notes.get("1.0", "end-1c"),
            }
            insert_row("environments", data)
            dialog.destroy()
            self.app.refresh_current_tab()

        ctk.CTkButton(scroll, text="💾 Save Environment", height=40,
                      fg_color=self.colors["accent"], command=save).pack(fill="x", pady=(15, 5))

    def _edit_env_dialog(self, env):
        dialog = ctk.CTkToplevel(self.parent)
        dialog.title(f"Edit: {env['name']}")
        dialog.geometry("480x550")
        dialog.transient(self.parent)
        dialog.after(50, lambda: dialog.grab_set())

        scroll = ctk.CTkScrollableFrame(dialog, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(scroll, text=f"Edit {env['name']}", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(0, 15))

        fields = {}
        env_types = ["Indoor Tent", "Indoor Room", "Greenhouse", "Outdoor", "Closet", "Cabinet"]

        def add_field(label, default="", options=None):
            ctk.CTkLabel(scroll, text=label, font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(8, 2))
            if options:
                var = ctk.StringVar(value=default)
                ctk.CTkOptionMenu(scroll, values=options, variable=var, width=380).pack(fill="x")
                fields[label] = var
            else:
                var = ctk.StringVar(value=default)
                ctk.CTkEntry(scroll, textvariable=var, width=380).pack(fill="x")
                fields[label] = var

        add_field("Name", env.get("name", ""))
        add_field("Type", env.get("env_type", "Indoor Tent"), env_types)
        add_field("Medium", env.get("medium", ""), MEDIUMS)
        add_field("Light Type", env.get("light_type", ""), LIGHT_TYPES)
        add_field("Light Wattage", str(env.get("light_wattage", "")))
        add_field("Light Schedule", env.get("light_schedule", "18/6"))
        add_field("Tent/Room Size", env.get("tent_size", ""))

        ctk.CTkLabel(scroll, text="Notes", font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(8, 2))
        notes = ctk.CTkTextbox(scroll, height=60, width=380)
        notes.pack(fill="x")
        notes.insert("1.0", env.get("notes", ""))

        self._edit_env_err = None

        def save():
            if self._edit_env_err:
                self._edit_env_err.destroy()
                self._edit_env_err = None

            name = fields["Name"].get().strip()
            err = validate_not_empty(name, "Name")
            if err:
                self._edit_env_err = show_validation_error(scroll, err, self.colors)
                return

            data = {
                "name": name,
                "env_type": fields["Type"].get(),
                "medium": fields["Medium"].get(),
                "light_type": fields["Light Type"].get(),
                "light_wattage": safe_int(fields["Light Wattage"].get(), 0),
                "light_schedule": fields["Light Schedule"].get(),
                "tent_size": fields["Tent/Room Size"].get(),
                "notes": notes.get("1.0", "end-1c"),
            }
            update_row("environments", env["id"], data)
            dialog.destroy()
            self.app.refresh_current_tab()

        ctk.CTkButton(scroll, text="💾 Save", height=40,
                      fg_color=self.colors["accent"], command=save).pack(fill="x", pady=(15, 5))

    def _delete_env(self, env):
        plants = get_plants_by_environment(env["id"])
        confirm = ctk.CTkToplevel(self.parent)
        confirm.title("Confirm Delete")
        confirm.geometry("420x170")
        confirm.transient(self.parent)
        confirm.after(50, lambda: confirm.grab_set())

        ctk.CTkLabel(
            confirm, text=f"Delete '{env['name']}'?",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(pady=(20, 5))

        if plants:
            ctk.CTkLabel(
                confirm,
                text=f"⚠️ {len(plants)} plant(s) are in this environment. "
                     "They will be unlinked but not deleted.",
                font=ctk.CTkFont(size=12),
                text_color=self.colors.get("warning", "#ff9800"),
                wraplength=380,
            ).pack(pady=5)
        else:
            ctk.CTkLabel(
                confirm, text="This environment has no plants.",
                font=ctk.CTkFont(size=12),
            ).pack(pady=5)

        bf = ctk.CTkFrame(confirm, fg_color="transparent")
        bf.pack(pady=10)

        ctk.CTkButton(
            bf, text="Cancel", width=120,
            fg_color=self.colors["bg_tertiary"],
            command=confirm.destroy,
        ).pack(side="left", padx=10)

        def do_delete():
            # Unlink plants from this environment
            from database import update_row as _upd
            for p in plants:
                _upd("plants", p["id"], {"environment_id": None})
            delete_row("environments", env["id"])
            confirm.destroy()
            self.app.refresh_current_tab()

        ctk.CTkButton(
            bf, text="🗑️ Delete", width=120,
            fg_color=self.colors["error"],
            command=do_delete,
        ).pack(side="left", padx=10)
