# FILE: growforge/ui/dashboard.py
"""
GrowForge — Dashboard tab with overview, stats, active plants, and reminders.
"""

import customtkinter as ctk
from datetime import datetime
from database import get_stats, get_active_plants, get_upcoming_reminders, get_recent_events
from config import STAGE_COLORS


class DashboardTab:
    """Main dashboard with quick stats, active plants, and upcoming reminders."""

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
        scroll.pack(fill="both", expand=True, padx=0, pady=0)

        # Header
        header = ctk.CTkFrame(scroll, fg_color="transparent")
        header.pack(fill="x", padx=25, pady=(20, 5))

        ctk.CTkLabel(
            header, text="📊 Dashboard",
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color=self.colors["fg_primary"],
        ).pack(side="left")

        ctk.CTkLabel(
            header, text=datetime.now().strftime("%A, %B %d, %Y"),
            font=ctk.CTkFont(size=13),
            text_color=self.colors["fg_muted"],
        ).pack(side="right", padx=10)

        # Stats cards
        stats = get_stats()
        cards_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        cards_frame.pack(fill="x", padx=25, pady=15)

        stat_items = [
            ("🌱", "Active Plants", stats.get("active_plants", 0)),
            ("🏠", "Environments", stats.get("environments", 0)),
            ("🌾", "Harvested", stats.get("total_harvested", 0)),
            ("⚖️", "Total Yield", f"{stats.get('total_yield', 0):.0f}g"),
            ("🧬", "Mothers", stats.get("mothers", 0)),
            ("🔬", "Crosses", stats.get("crosses", 0)),
            ("📝", "Journal Entries", stats.get("total_events", 0)),
            ("🔔", "Reminders", stats.get("pending_reminders", 0)),
        ]

        for i, (icon, label, value) in enumerate(stat_items):
            card = ctk.CTkFrame(
                cards_frame, fg_color=self.colors["bg_card"],
                corner_radius=12, height=90,
            )
            card.grid(row=i // 4, column=i % 4, padx=6, pady=6, sticky="nsew")
            cards_frame.grid_columnconfigure(i % 4, weight=1)

            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(expand=True, fill="both", padx=15, pady=12)

            ctk.CTkLabel(
                inner, text=f"{icon} {label}",
                font=ctk.CTkFont(size=11),
                text_color=self.colors["fg_muted"],
            ).pack(anchor="w")

            ctk.CTkLabel(
                inner, text=str(value),
                font=ctk.CTkFont(size=28, weight="bold"),
                text_color=self.colors["accent"],
            ).pack(anchor="w", pady=(2, 0))

        # Two-column layout
        columns = ctk.CTkFrame(scroll, fg_color="transparent")
        columns.pack(fill="both", expand=True, padx=25, pady=10)
        columns.grid_columnconfigure(0, weight=3)
        columns.grid_columnconfigure(1, weight=2)

        # ─── Active Plants ──────────────────────────────────────────────
        plants_card = ctk.CTkFrame(columns, fg_color=self.colors["bg_card"], corner_radius=12)
        plants_card.grid(row=0, column=0, padx=(0, 8), pady=5, sticky="nsew")

        ctk.CTkLabel(
            plants_card, text="🌱 Active Plants",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors["fg_primary"],
        ).pack(anchor="w", padx=18, pady=(15, 10))

        plants = get_active_plants()
        if plants:
            for plant in plants[:8]:
                pf = ctk.CTkFrame(plants_card, fg_color=self.colors["bg_secondary"], corner_radius=8)
                pf.pack(fill="x", padx=15, pady=3)

                info = ctk.CTkFrame(pf, fg_color="transparent")
                info.pack(fill="x", padx=12, pady=8)

                sc = STAGE_COLORS.get(plant.get("stage", ""), "#888888")

                name_row = ctk.CTkFrame(info, fg_color="transparent")
                name_row.pack(fill="x")

                ctk.CTkLabel(
                    name_row, text=plant.get("name", "?"),
                    font=ctk.CTkFont(size=14, weight="bold"),
                    text_color=self.colors["fg_primary"],
                ).pack(side="left")

                badge = ctk.CTkLabel(
                    name_row, text=f" {plant.get('stage', '?')} ",
                    font=ctk.CTkFont(size=10),
                    text_color="#ffffff",
                    fg_color=sc,
                    corner_radius=4,
                )
                badge.pack(side="right")

                strain_info = plant.get('strain_name', 'Unknown strain')
                detail_text = f"{strain_info} • {plant.get('plant_type', 'Photo')}"
                if plant.get("start_date"):
                    try:
                        start = datetime.strptime(plant["start_date"], "%Y-%m-%d")
                        days = (datetime.now() - start).days
                        detail_text += f" • Day {days}"
                    except ValueError:
                        pass

                ctk.CTkLabel(
                    info, text=detail_text,
                    font=ctk.CTkFont(size=11),
                    text_color=self.colors["fg_muted"],
                ).pack(anchor="w")
        else:
            ctk.CTkLabel(
                plants_card, text="No active plants. Add one in the Plants tab!",
                font=ctk.CTkFont(size=12),
                text_color=self.colors["fg_muted"],
            ).pack(padx=18, pady=20)

        # ─── Reminders & Recent Activity ────────────────────────────────
        right_col = ctk.CTkFrame(columns, fg_color="transparent")
        right_col.grid(row=0, column=1, padx=(8, 0), pady=5, sticky="nsew")

        # Upcoming Reminders
        rem_card = ctk.CTkFrame(right_col, fg_color=self.colors["bg_card"], corner_radius=12)
        rem_card.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            rem_card, text="🔔 Upcoming Reminders",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors["fg_primary"],
        ).pack(anchor="w", padx=18, pady=(15, 10))

        reminders = get_upcoming_reminders(7)
        if reminders:
            for rem in reminders[:6]:
                rf = ctk.CTkFrame(rem_card, fg_color=self.colors["bg_secondary"], corner_radius=6)
                rf.pack(fill="x", padx=15, pady=2)

                ri = ctk.CTkFrame(rf, fg_color="transparent")
                ri.pack(fill="x", padx=10, pady=6)

                due = rem.get("due_date", "")[:10]
                ctk.CTkLabel(
                    ri, text=rem.get("message", "Reminder"),
                    font=ctk.CTkFont(size=12),
                    text_color=self.colors["fg_primary"],
                ).pack(anchor="w")
                ctk.CTkLabel(
                    ri, text=f"Due: {due} • {rem.get('reminder_type', '')}",
                    font=ctk.CTkFont(size=10),
                    text_color=self.colors["fg_muted"],
                ).pack(anchor="w")
        else:
            ctk.CTkLabel(
                rem_card, text="No upcoming reminders",
                text_color=self.colors["fg_muted"], font=ctk.CTkFont(size=12),
            ).pack(padx=18, pady=15)

        # Recent Activity
        act_card = ctk.CTkFrame(right_col, fg_color=self.colors["bg_card"], corner_radius=12)
        act_card.pack(fill="x")

        ctk.CTkLabel(
            act_card, text="📝 Recent Activity",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors["fg_primary"],
        ).pack(anchor="w", padx=18, pady=(15, 10))

        events = get_recent_events(6)
        if events:
            for ev in events:
                ef = ctk.CTkFrame(act_card, fg_color=self.colors["bg_secondary"], corner_radius=6)
                ef.pack(fill="x", padx=15, pady=2)
                ei = ctk.CTkFrame(ef, fg_color="transparent")
                ei.pack(fill="x", padx=10, pady=5)

                date = ev.get("event_date", "")[:10]
                plant_name = ev.get("plant_name", "")
                etype = ev.get("event_type", "")

                ctk.CTkLabel(
                    ei, text=f"{etype} — {plant_name}",
                    font=ctk.CTkFont(size=11),
                    text_color=self.colors["fg_primary"],
                ).pack(anchor="w")
                ctk.CTkLabel(
                    ei, text=date,
                    font=ctk.CTkFont(size=10),
                    text_color=self.colors["fg_muted"],
                ).pack(anchor="w")
        else:
            ctk.CTkLabel(
                act_card, text="No recent activity",
                text_color=self.colors["fg_muted"], font=ctk.CTkFont(size=12),
            ).pack(padx=18, pady=15)
