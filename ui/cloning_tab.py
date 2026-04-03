# FILE: growforge/ui/cloning_tab.py
"""
GrowForge — Cloning Station tab: mother management, clone batches, tracking.
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

    def _build(self):
        scroll = ctk.CTkScrollableFrame(self.parent, fg_color="transparent",
                                         scrollbar_button_color=self.colors["bg_tertiary"])
        scroll.pack(fill="both", expand=True)

        header = ctk.CTkFrame(scroll, fg_color="transparent")
        header.pack(fill="x", padx=25, pady=(20, 10))

        ctk.CTkLabel(header, text="🧬 Cloning Station",
                     font=ctk.CTkFont(size=26, weight="bold"),
                     text_color=self.colors["fg_primary"]).pack(side="left")

        ctk.CTkButton(header, text="➕ New Batch", width=130, height=36,
                      fg_color=self.colors["accent"], hover_color=self.colors["accent_hover"],
                      font=ctk.CTkFont(size=13),
                      command=self._new_batch_dialog).pack(side="right")

        # Mother plants section
        mothers = get_mother_plants()
        ctk.CTkLabel(scroll, text="👑 Mother Plants",
                     font=ctk.CTkFont(size=18, weight="bold"),
                     text_color=self.colors["fg_primary"]).pack(anchor="w", padx=25, pady=(15, 5))

        if mothers:
            for m in mothers:
                mf = ctk.CTkFrame(scroll, fg_color=self.colors["bg_card"], corner_radius=10)
                mf.pack(fill="x", padx=25, pady=3)
                mi = ctk.CTkFrame(mf, fg_color="transparent")
                mi.pack(fill="x", padx=15, pady=10)

                ctk.CTkLabel(mi, text=f"👑 {m['name']}",
                            font=ctk.CTkFont(size=14, weight="bold"),
                            text_color=self.colors["fg_primary"]).pack(side="left")

                strain = m.get("strain_name", "Unknown")
                batches = get_clone_batches(m["id"])
                total_clones = sum(b.get("num_cuts", 0) for b in batches)

                ctk.CTkLabel(mi, text=f"{strain} • {len(batches)} batches • {total_clones} total clones",
                            font=ctk.CTkFont(size=11),
                            text_color=self.colors["fg_muted"]).pack(side="right")
        else:
            ctk.CTkLabel(scroll, text="No mother plants. Designate a plant as mother in the Plants tab.",
                        text_color=self.colors["fg_muted"], font=ctk.CTkFont(size=12)).pack(padx=25, pady=10)

        # Clone batches
        ctk.CTkLabel(scroll, text="🌿 Clone Batches",
                     font=ctk.CTkFont(size=18, weight="bold"),
                     text_color=self.colors["fg_primary"]).pack(anchor="w", padx=25, pady=(20, 5))

        batches = get_clone_batches()
        if batches:
            for batch in batches:
                self._batch_card(scroll, batch)
        else:
            ctk.CTkLabel(scroll, text="No clone batches yet. Click 'New Batch' to start.",
                        text_color=self.colors["fg_muted"], font=ctk.CTkFont(size=12)).pack(padx=25, pady=10)

        # Cloning guide
        ctk.CTkLabel(scroll, text="📖 Cloning Quick Guide",
                     font=ctk.CTkFont(size=18, weight="bold"),
                     text_color=self.colors["fg_primary"]).pack(anchor="w", padx=25, pady=(20, 5))

        for section, data in CLONING_GUIDE.items():
            if "title" not in data or "tips" not in data:
                continue
            gf = ctk.CTkFrame(scroll, fg_color=self.colors["bg_card"], corner_radius=10)
            gf.pack(fill="x", padx=25, pady=3)
            gi = ctk.CTkFrame(gf, fg_color="transparent")
            gi.pack(fill="x", padx=15, pady=10)

            ctk.CTkLabel(gi, text=data["title"],
                        font=ctk.CTkFont(size=14, weight="bold"),
                        text_color=self.colors["accent"]).pack(anchor="w")

            for tip in data["tips"][:4]:
                ctk.CTkLabel(gi, text=f"  • {tip}",
                            font=ctk.CTkFont(size=11),
                            text_color=self.colors["fg_secondary"],
                            wraplength=700, justify="left").pack(anchor="w")

    def _batch_card(self, parent, batch):
        card = ctk.CTkFrame(parent, fg_color=self.colors["bg_card"], corner_radius=10)
        card.pack(fill="x", padx=25, pady=4)
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=15, pady=10)

        top = ctk.CTkFrame(inner, fg_color="transparent")
        top.pack(fill="x")

        ctk.CTkLabel(top, text=f"🌿 {batch['batch_name']}",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=self.colors["fg_primary"]).pack(side="left")

        ctk.CTkLabel(top, text=f"Cut: {batch.get('cut_date', 'N/A')} • {batch.get('num_cuts', 0)} cuts",
                     font=ctk.CTkFont(size=11),
                     text_color=self.colors["fg_muted"]).pack(side="right")

        details = []
        if batch.get("rooting_method"): details.append(batch["rooting_method"])
        if batch.get("medium"): details.append(batch["medium"])
        if details:
            ctk.CTkLabel(inner, text=" • ".join(details),
                        font=ctk.CTkFont(size=11),
                        text_color=self.colors["fg_secondary"]).pack(anchor="w", pady=(3, 0))

        # Clone status summary
        clones = get_clones_in_batch(batch["id"])
        if clones:
            active = sum(1 for c in clones if c.get("status") == "Active")
            dead = sum(1 for c in clones if c.get("status") == "Dead")
            promoted = sum(1 for c in clones if c.get("status") == "Promoted")

            summary_parts = []
            if active: summary_parts.append(f"🟢 {active} active")
            if dead: summary_parts.append(f"🔴 {dead} dead")
            if promoted: summary_parts.append(f"🔵 {promoted} promoted")

            if summary_parts:
                ctk.CTkLabel(inner, text="  ".join(summary_parts),
                            font=ctk.CTkFont(size=11),
                            text_color=self.colors["fg_primary"]).pack(anchor="w", pady=(3, 0))

            # Individual clones
            clones_f = ctk.CTkFrame(inner, fg_color="transparent")
            clones_f.pack(fill="x", pady=(5, 0))

            for clone in clones:
                status_colors = {"Active": self.colors["success"], "Dead": self.colors["error"],
                                "Promoted": self.colors["info"]}
                sc = status_colors.get(clone.get("status", ""), self.colors["fg_muted"])

                cf = ctk.CTkFrame(clones_f, fg_color=self.colors["bg_secondary"], corner_radius=6)
                cf.pack(fill="x", pady=1)
                ci = ctk.CTkFrame(cf, fg_color="transparent")
                ci.pack(fill="x", padx=10, pady=4)

                ctk.CTkLabel(ci, text=clone["clone_name"],
                            font=ctk.CTkFont(size=11),
                            text_color=self.colors["fg_primary"]).pack(side="left")

                ctk.CTkLabel(ci, text=f"{clone.get('stage', '?')} • {clone.get('status', '?')}",
                            font=ctk.CTkFont(size=10), text_color=sc).pack(side="right")

        # Buttons
        btns = ctk.CTkFrame(inner, fg_color="transparent")
        btns.pack(fill="x", pady=(6, 0))

        ctk.CTkButton(btns, text="✏️ Update Clones", width=130, height=28,
                      font=ctk.CTkFont(size=11),
                      fg_color=self.colors["bg_tertiary"],
                      hover_color=self.colors["highlight"],
                      command=lambda b=batch: self._update_clones_dialog(b)).pack(side="left", padx=(0, 5))

        ctk.CTkButton(btns, text="🗑️ Delete Batch", width=110, height=28,
                      font=ctk.CTkFont(size=11),
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
