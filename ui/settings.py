# FILE: growforge/ui/settings.py
"""
GrowForge — Settings tab: theme, backup/restore, export, preferences.
"""

import customtkinter as ctk
import shutil
import os
from datetime import datetime
from config import DB_PATH, BACKUP_DIR, EXPORT_DIR, APP_VERSION
from database import (
    get_setting, set_setting, get_all, get_active_plants,
    get_recent_events,
)
from utils.exporters import export_all_data, export_plant_report
from knowledge_base import GLOSSARY


class SettingsTab:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.colors = app.colors
        self._build()

    def _build(self):
        scroll = ctk.CTkScrollableFrame(self.parent, fg_color="transparent",
                                         scrollbar_button_color=self.colors["bg_tertiary"])
        scroll.pack(fill="both", expand=True)

        ctk.CTkLabel(scroll, text="⚙️ Settings",
                     font=ctk.CTkFont(size=26, weight="bold"),
                     text_color=self.colors["fg_primary"]).pack(anchor="w", padx=25, pady=(20, 15))

        # ─── Appearance ─────────────────────────────────────────────────
        self._section(scroll, "🎨 Appearance")

        theme_card = ctk.CTkFrame(scroll, fg_color=self.colors["bg_card"], corner_radius=12)
        theme_card.pack(fill="x", padx=25, pady=5)
        ti = ctk.CTkFrame(theme_card, fg_color="transparent")
        ti.pack(fill="x", padx=18, pady=12)

        ctk.CTkLabel(ti, text="Theme", font=ctk.CTkFont(size=14),
                    text_color=self.colors["fg_primary"]).pack(side="left")

        current_theme = get_setting("theme", "dark")
        theme_var = ctk.StringVar(value=current_theme.title())

        def change_theme(choice):
            theme = choice.lower()
            self.app.switch_theme(theme)

        ctk.CTkOptionMenu(ti, values=["Dark", "Light"], variable=theme_var,
                          width=120, command=change_theme).pack(side="right")

        # Mode
        mode_card = ctk.CTkFrame(scroll, fg_color=self.colors["bg_card"], corner_radius=12)
        mode_card.pack(fill="x", padx=25, pady=5)
        mi = ctk.CTkFrame(mode_card, fg_color="transparent")
        mi.pack(fill="x", padx=18, pady=12)

        ctk.CTkLabel(mi, text="Mode", font=ctk.CTkFont(size=14),
                    text_color=self.colors["fg_primary"]).pack(side="left")

        current_mode = get_setting("mode", "beginner")
        mode_var = ctk.StringVar(value=current_mode.title())

        def change_mode(choice):
            set_setting("mode", choice.lower())

        ctk.CTkOptionMenu(mi, values=["Beginner", "Advanced"], variable=mode_var,
                          width=140, command=change_mode).pack(side="right")

        ctk.CTkLabel(mi, text="(Beginner shows more guidance tooltips)",
                    font=ctk.CTkFont(size=10), text_color=self.colors["fg_muted"]).pack(side="right", padx=10)

        # ─── Backup & Restore ───────────────────────────────────────────
        self._section(scroll, "💾 Backup & Restore")

        backup_card = ctk.CTkFrame(scroll, fg_color=self.colors["bg_card"], corner_radius=12)
        backup_card.pack(fill="x", padx=25, pady=5)
        bi = ctk.CTkFrame(backup_card, fg_color="transparent")
        bi.pack(fill="x", padx=18, pady=12)

        ctk.CTkButton(bi, text="📦 Backup Database", width=180, height=36,
                      fg_color=self.colors["accent"],
                      hover_color=self.colors["accent_hover"],
                      command=self._backup_db).pack(side="left", padx=(0, 10))

        ctk.CTkButton(bi, text="📂 Restore from Backup", width=180, height=36,
                      fg_color=self.colors["bg_tertiary"],
                      hover_color=self.colors["highlight"],
                      command=self._restore_db).pack(side="left")

        self.backup_status = ctk.CTkLabel(bi, text="", font=ctk.CTkFont(size=11),
                                           text_color=self.colors["success"])
        self.backup_status.pack(side="right")

        # Show existing backups
        backups = sorted(BACKUP_DIR.glob("*.db"), reverse=True)
        if backups:
            ctk.CTkLabel(backup_card, text=f"  Latest backup: {backups[0].name}",
                        font=ctk.CTkFont(size=10),
                        text_color=self.colors["fg_muted"]).pack(anchor="w", padx=18, pady=(0, 8))

        # ─── Export ─────────────────────────────────────────────────────
        self._section(scroll, "📊 Export Data")

        export_card = ctk.CTkFrame(scroll, fg_color=self.colors["bg_card"], corner_radius=12)
        export_card.pack(fill="x", padx=25, pady=5)
        ei = ctk.CTkFrame(export_card, fg_color="transparent")
        ei.pack(fill="x", padx=18, pady=12)

        ctk.CTkButton(ei, text="📄 Export All as CSV", width=170, height=36,
                      fg_color=self.colors["accent"],
                      command=self._export_csv).pack(side="left", padx=(0, 10))

        ctk.CTkButton(ei, text="📑 Export PDF Report", width=170, height=36,
                      fg_color=self.colors["accent_dark"],
                      command=self._export_pdf_dialog).pack(side="left")

        self.export_status = ctk.CTkLabel(ei, text="", font=ctk.CTkFont(size=11),
                                           text_color=self.colors["success"])
        self.export_status.pack(side="right")

        ctk.CTkLabel(export_card, text=f"  Export folder: {EXPORT_DIR}",
                    font=ctk.CTkFont(size=10),
                    text_color=self.colors["fg_muted"]).pack(anchor="w", padx=18, pady=(0, 8))

        # ─── Glossary ───────────────────────────────────────────────────
        self._section(scroll, "📖 Cannabis Glossary")

        glossary_card = ctk.CTkFrame(scroll, fg_color=self.colors["bg_card"], corner_radius=12)
        glossary_card.pack(fill="x", padx=25, pady=5)
        gli = ctk.CTkFrame(glossary_card, fg_color="transparent")
        gli.pack(fill="x", padx=18, pady=12)

        for term, definition in sorted(GLOSSARY.items()):
            tf = ctk.CTkFrame(gli, fg_color="transparent")
            tf.pack(fill="x", pady=2)

            ctk.CTkLabel(tf, text=f"  {term}",
                        font=ctk.CTkFont(size=12, weight="bold"),
                        text_color=self.colors["accent"]).pack(anchor="w")
            ctk.CTkLabel(tf, text=f"    {definition}",
                        font=ctk.CTkFont(size=11),
                        text_color=self.colors["fg_secondary"],
                        wraplength=700, justify="left").pack(anchor="w")

        # ─── About ─────────────────────────────────────────────────────
        self._section(scroll, "ℹ️ About")

        about_card = ctk.CTkFrame(scroll, fg_color=self.colors["bg_card"], corner_radius=12)
        about_card.pack(fill="x", padx=25, pady=5)
        ai_about = ctk.CTkFrame(about_card, fg_color="transparent")
        ai_about.pack(fill="x", padx=18, pady=12)

        ctk.CTkLabel(ai_about, text=f"🌿 GrowForge v{APP_VERSION}",
                    font=ctk.CTkFont(size=16, weight="bold"),
                    text_color=self.colors["accent"]).pack(anchor="w")
        ctk.CTkLabel(ai_about, text="From Seed to Harvest, Clone to Cross",
                    font=ctk.CTkFont(size=12),
                    text_color=self.colors["fg_muted"]).pack(anchor="w", pady=(2, 5))
        ctk.CTkLabel(ai_about, text="100% local-first • No cloud • No accounts • Your data stays yours",
                    font=ctk.CTkFont(size=11),
                    text_color=self.colors["fg_secondary"]).pack(anchor="w")
        ctk.CTkLabel(ai_about, text=f"Database: {DB_PATH}",
                    font=ctk.CTkFont(size=10),
                    text_color=self.colors["fg_muted"]).pack(anchor="w", pady=(5, 0))

    def _section(self, parent, title):
        ctk.CTkLabel(parent, text=title,
                     font=ctk.CTkFont(size=18, weight="bold"),
                     text_color=self.colors["fg_primary"]).pack(anchor="w", padx=25, pady=(18, 5))

    def _backup_db(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = BACKUP_DIR / f"growforge_backup_{timestamp}.db"
        try:
            shutil.copy2(str(DB_PATH), str(backup_path))
            self.backup_status.configure(text=f"✅ Backed up to {backup_path.name}")
        except Exception as e:
            self.backup_status.configure(text=f"❌ Error: {e}", text_color=self.colors["error"])

    def _restore_db(self):
        backups = sorted(BACKUP_DIR.glob("*.db"), reverse=True)
        if not backups:
            self.backup_status.configure(text="❌ No backups found", text_color=self.colors["error"])
            return

        # Let user pick from available backups
        dialog = ctk.CTkToplevel(self.parent)
        dialog.title("Restore from Backup")
        dialog.geometry("450x280")
        dialog.transient(self.parent)
        dialog.after(50, lambda: dialog.grab_set())

        ctk.CTkLabel(dialog, text="⚠️ Restore Database",
                    font=ctk.CTkFont(size=16, weight="bold"),
                    text_color=self.colors["warning"]).pack(pady=(20, 5))
        ctk.CTkLabel(dialog, text="This will REPLACE your current database.\nA backup of the current DB will be made first.",
                    font=ctk.CTkFont(size=12),
                    text_color=self.colors["fg_secondary"]).pack(pady=(0, 10))

        backup_names = [b.name for b in backups[:10]]
        backup_var = ctk.StringVar(value=backup_names[0])
        ctk.CTkOptionMenu(dialog, values=backup_names, variable=backup_var, width=380).pack(pady=5)

        bf = ctk.CTkFrame(dialog, fg_color="transparent")
        bf.pack(pady=15)

        ctk.CTkButton(bf, text="Cancel", width=120,
                      fg_color=self.colors["bg_tertiary"],
                      command=dialog.destroy).pack(side="left", padx=10)

        def do_restore():
            selected = backup_var.get()
            selected_path = BACKUP_DIR / selected
            try:
                # Auto-backup current DB before restoring
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                pre_restore = BACKUP_DIR / f"growforge_pre_restore_{timestamp}.db"
                shutil.copy2(str(DB_PATH), str(pre_restore))
                # Restore
                shutil.copy2(str(selected_path), str(DB_PATH))
                dialog.destroy()
                self.backup_status.configure(
                    text=f"✅ Restored from {selected}. Restart app to apply!")
            except Exception as e:
                dialog.destroy()
                self.backup_status.configure(
                    text=f"❌ Restore error: {e}", text_color=self.colors["error"])

        ctk.CTkButton(bf, text="🔄 Restore", width=120,
                      fg_color=self.colors["warning"],
                      hover_color=self.colors["error"],
                      command=do_restore).pack(side="left", padx=10)

    def _export_csv(self):
        try:
            plants = get_all("plants")
            events = get_all("events")
            envs = get_all("environments")
            strains = get_all("strains")

            files = export_all_data(plants, events, envs, strains)
            self.export_status.configure(text=f"✅ Exported {len(files)} files to exports/")
        except Exception as e:
            self.export_status.configure(text=f"❌ Error: {e}", text_color=self.colors["error"])

    def _export_pdf_dialog(self):
        plants = get_active_plants() + get_all("plants", where="stage='Harvested'")
        if not plants:
            self.export_status.configure(text="❌ No plants to export", text_color=self.colors["error"])
            return

        dialog = ctk.CTkToplevel(self.parent)
        dialog.title("Export PDF Report")
        dialog.geometry("400x300")
        dialog.transient(self.parent)
        dialog.after(50, lambda: dialog.grab_set())

        ctk.CTkLabel(dialog, text="Select Plant for PDF Report",
                     font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(20, 10))

        plant_options = [f"{p['name']} (#{p['id']})" for p in plants]
        plant_var = ctk.StringVar(value=plant_options[0])
        ctk.CTkOptionMenu(dialog, values=plant_options, variable=plant_var, width=300).pack(pady=5)

        def generate():
            try:
                pid = int(plant_var.get().split("#")[1].rstrip(")"))
                from database import get_row, get_plant_events
                plant = get_row("plants", pid)
                events = get_plant_events(pid)
                env = get_row("environments", plant["environment_id"]) if plant.get("environment_id") else None
                filepath = export_plant_report(plant, events, env)
                dialog.destroy()
                self.export_status.configure(text=f"✅ PDF saved: {os.path.basename(filepath)}")
            except Exception as e:
                self.export_status.configure(text=f"❌ Error: {e}", text_color=self.colors["error"])
                dialog.destroy()

        ctk.CTkButton(dialog, text="📑 Generate PDF", width=200, height=40,
                      fg_color=self.colors["accent"], command=generate).pack(pady=20)
