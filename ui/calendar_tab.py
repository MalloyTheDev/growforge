# FILE: growforge/ui/calendar_tab.py
"""
GrowForge — Calendar view with events and reminders overlaid.
Click on a day to see full event details. Mark reminders as complete.
"""

import customtkinter as ctk
from datetime import datetime, timedelta
from database import get_all, get_active_plants, get_upcoming_reminders, update_row


class CalendarTab:
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

        ctk.CTkLabel(header, text="📅 Calendar & Schedule",
                     font=ctk.CTkFont(size=26, weight="bold"),
                     text_color=self.colors["fg_primary"]).pack(side="left")

        # Current month display
        now = datetime.now()
        self.current_month = now.month
        self.current_year = now.year

        nav = ctk.CTkFrame(scroll, fg_color="transparent")
        nav.pack(fill="x", padx=25, pady=5)

        ctk.CTkButton(nav, text="◀", width=40, height=32,
                      fg_color=self.colors["bg_tertiary"],
                      hover_color=self.colors["highlight"],
                      command=self._prev_month).pack(side="left")

        self.month_label = ctk.CTkLabel(nav, text="",
                                        font=ctk.CTkFont(size=18, weight="bold"),
                                        text_color=self.colors["fg_primary"])
        self.month_label.pack(side="left", padx=15)

        ctk.CTkButton(nav, text="▶", width=40, height=32,
                      fg_color=self.colors["bg_tertiary"],
                      hover_color=self.colors["highlight"],
                      command=self._next_month).pack(side="left")

        ctk.CTkButton(nav, text="📍 Today", width=90, height=32,
                      fg_color=self.colors["accent"],
                      hover_color=self.colors["accent_hover"],
                      font=ctk.CTkFont(size=12),
                      command=self._go_today).pack(side="right")

        # Calendar grid
        self.cal_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        self.cal_frame.pack(fill="x", padx=25, pady=10)

        # Events section
        self.events_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        self.events_frame.pack(fill="x", padx=25, pady=10)

        self._render_calendar()

    def _render_calendar(self):
        for w in self.cal_frame.winfo_children():
            w.destroy()
        for w in self.events_frame.winfo_children():
            w.destroy()

        import calendar
        cal = calendar.Calendar(firstweekday=6)
        month_name = calendar.month_name[self.current_month]
        self.month_label.configure(text=f"{month_name} {self.current_year}")

        # Day headers
        days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
        for i, day in enumerate(days):
            ctk.CTkLabel(self.cal_frame, text=day,
                        font=ctk.CTkFont(size=12, weight="bold"),
                        text_color=self.colors["fg_muted"]).grid(row=0, column=i, padx=2, pady=5)

        # Get events for this month
        month_str = f"{self.current_year}-{self.current_month:02d}"
        events_by_date = {}
        all_events = get_all("events",
                             where="event_date LIKE ?",
                             params=[f"{month_str}%"])
        for ev in all_events:
            d = ev.get("event_date", "")[:10]
            events_by_date.setdefault(d, []).append(ev)

        # Get reminders
        reminders_by_date = {}
        all_reminders = get_all("reminders",
                           where="due_date LIKE ? AND is_completed=0",
                           params=[f"{month_str}%"])
        for rem in all_reminders:
            d = rem.get("due_date", "")[:10]
            reminders_by_date.setdefault(d, []).append(rem)
            events_by_date.setdefault(d, []).append(
                {"event_type": f"🔔 {rem.get('message', 'Reminder')}", "_is_reminder": True}
            )

        # Render days
        today = datetime.now()
        weeks = cal.monthdayscalendar(self.current_year, self.current_month)

        for week_idx, week in enumerate(weeks):
            for day_idx, day in enumerate(week):
                if day == 0:
                    ctk.CTkLabel(self.cal_frame, text="",
                                width=120, height=75).grid(row=week_idx + 1, column=day_idx, padx=2, pady=2)
                    continue

                date_str = f"{self.current_year}-{self.current_month:02d}-{day:02d}"
                is_today = (day == today.day and self.current_month == today.month
                           and self.current_year == today.year)

                day_events = events_by_date.get(date_str, [])
                day_reminders = reminders_by_date.get(date_str, [])
                has_events = len(day_events) > 0

                if is_today:
                    bg = self.colors["accent_dark"]
                elif has_events:
                    bg = self.colors["bg_secondary"]
                else:
                    bg = self.colors["bg_card"]

                cell = ctk.CTkFrame(self.cal_frame, fg_color=bg, corner_radius=8,
                                    width=120, height=75)
                cell.grid(row=week_idx + 1, column=day_idx, padx=2, pady=2, sticky="nsew")
                cell.grid_propagate(False)
                self.cal_frame.grid_columnconfigure(day_idx, weight=1)

                # Make cell clickable if it has events
                if has_events:
                    cell.bind("<Button-1>", lambda e, ds=date_str, de=day_events, dr=day_reminders: self._show_day_detail(ds, de, dr))
                    cell.configure(cursor="hand2")

                # Day number with event count indicator
                day_top = ctk.CTkFrame(cell, fg_color="transparent")
                day_top.pack(fill="x", padx=6, pady=3)
                if has_events:
                    day_top.bind("<Button-1>", lambda e, ds=date_str, de=day_events, dr=day_reminders: self._show_day_detail(ds, de, dr))

                ctk.CTkLabel(day_top, text=str(day),
                            font=ctk.CTkFont(size=13, weight="bold" if is_today else "normal"),
                            text_color=self.colors["fg_primary"]).pack(side="left")

                if has_events:
                    count = len(day_events)
                    ctk.CTkLabel(day_top, text=f"({count})",
                                font=ctk.CTkFont(size=9),
                                text_color=self.colors["accent"]).pack(side="right")

                for ev in day_events[:2]:
                    etype = ev.get("event_type", "")[:18]
                    color = self.colors["warning"] if ev.get("_is_reminder") else self.colors["accent"]
                    lbl = ctk.CTkLabel(cell, text=etype,
                                font=ctk.CTkFont(size=9),
                                text_color=color)
                    lbl.pack(anchor="w", padx=6)
                    if has_events:
                        lbl.bind("<Button-1>", lambda e, ds=date_str, de=day_events, dr=day_reminders: self._show_day_detail(ds, de, dr))

                if len(day_events) > 2:
                    more_lbl = ctk.CTkLabel(cell, text=f"+{len(day_events)-2} more",
                                font=ctk.CTkFont(size=8),
                                text_color=self.colors["fg_muted"])
                    more_lbl.pack(anchor="w", padx=6)
                    if has_events:
                        more_lbl.bind("<Button-1>", lambda e, ds=date_str, de=day_events, dr=day_reminders: self._show_day_detail(ds, de, dr))

        # ─── Upcoming section (reminders + events) ────────────────────────
        ctk.CTkLabel(self.events_frame, text="📋 Upcoming This Month",
                     font=ctk.CTkFont(size=16, weight="bold"),
                     text_color=self.colors["fg_primary"]).pack(anchor="w", pady=(10, 5))

        # Combine reminders and recent events
        upcoming_reminders = get_upcoming_reminders(30)
        has_upcoming = False

        if upcoming_reminders:
            has_upcoming = True
            for rem in upcoming_reminders[:8]:
                rf = ctk.CTkFrame(self.events_frame, fg_color=self.colors["bg_card"], corner_radius=8)
                rf.pack(fill="x", pady=2)
                ri = ctk.CTkFrame(rf, fg_color="transparent")
                ri.pack(fill="x", padx=12, pady=6)

                due = rem.get("due_date", "")[:10]
                ctk.CTkLabel(ri, text=f"🔔 {rem.get('message', '')}",
                            font=ctk.CTkFont(size=12),
                            text_color=self.colors["fg_primary"]).pack(side="left")

                # Complete button
                rem_id = rem.get("id")
                if rem_id:
                    ctk.CTkButton(ri, text="✅ Done", width=70, height=24,
                                 font=ctk.CTkFont(size=10),
                                 fg_color=self.colors["success"],
                                 hover_color=self.colors["accent"],
                                 command=lambda rid=rem_id: self._complete_reminder(rid)
                                 ).pack(side="right", padx=(5, 0))

                ctk.CTkLabel(ri, text=due,
                            font=ctk.CTkFont(size=11),
                            text_color=self.colors["fg_muted"]).pack(side="right")

        # Show upcoming events too
        today_str = datetime.now().strftime("%Y-%m-%d")
        upcoming_events = get_all("events",
                                  where="event_date >= ?",
                                  params=[today_str],
                                  order="event_date ASC")
        if upcoming_events:
            has_upcoming = True
            shown = 0
            for ev in upcoming_events:
                if shown >= 6:
                    break
                ef = ctk.CTkFrame(self.events_frame, fg_color=self.colors["bg_card"], corner_radius=8)
                ef.pack(fill="x", pady=2)
                ei = ctk.CTkFrame(ef, fg_color="transparent")
                ei.pack(fill="x", padx=12, pady=6)

                ev_date = ev.get("event_date", "")[:10]
                etype = ev.get("event_type", "")
                ctk.CTkLabel(ei, text=f"📝 {etype}",
                            font=ctk.CTkFont(size=12),
                            text_color=self.colors["fg_primary"]).pack(side="left")
                ctk.CTkLabel(ei, text=ev_date,
                            font=ctk.CTkFont(size=11),
                            text_color=self.colors["fg_muted"]).pack(side="right")
                shown += 1

        if not has_upcoming:
            ctk.CTkLabel(self.events_frame, text="No upcoming events or reminders",
                        text_color=self.colors["fg_muted"]).pack(pady=10)

    def _show_day_detail(self, date_str, events, reminders):
        dialog = ctk.CTkToplevel(self.parent)
        dialog.title(f"Events — {date_str}")
        dialog.geometry("480x400")
        dialog.transient(self.parent)
        dialog.after(50, lambda: dialog.grab_set())

        scroll = ctk.CTkScrollableFrame(dialog, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=15, pady=15)

        ctk.CTkLabel(scroll, text=f"📅 {date_str}",
                    font=ctk.CTkFont(size=18, weight="bold"),
                    text_color=self.colors["fg_primary"]).pack(anchor="w", pady=(0, 10))

        # Show real events (not reminder placeholders)
        real_events = [e for e in events if not e.get("_is_reminder")]
        if real_events:
            ctk.CTkLabel(scroll, text="Events",
                        font=ctk.CTkFont(size=14, weight="bold"),
                        text_color=self.colors["accent"]).pack(anchor="w", pady=(5, 3))

            for ev in real_events:
                ef = ctk.CTkFrame(scroll, fg_color=self.colors["bg_card"], corner_radius=8)
                ef.pack(fill="x", pady=3)
                ei = ctk.CTkFrame(ef, fg_color="transparent")
                ei.pack(fill="x", padx=12, pady=8)

                etype = ev.get("event_type", "Unknown")
                time_str = ev.get("event_date", "")[11:16] if len(ev.get("event_date", "")) > 11 else ""
                ctk.CTkLabel(ei, text=f"📝 {etype}" + (f"  ({time_str})" if time_str else ""),
                            font=ctk.CTkFont(size=13, weight="bold"),
                            text_color=self.colors["fg_primary"]).pack(anchor="w")

                # Show metrics
                metrics = []
                if ev.get("ph"): metrics.append(f"pH {ev['ph']}")
                if ev.get("ec"): metrics.append(f"EC {ev['ec']}")
                if ev.get("temp"): metrics.append(f"{ev['temp']}°C")
                if ev.get("humidity"): metrics.append(f"{ev['humidity']}% RH")
                if ev.get("water_ml"): metrics.append(f"{ev['water_ml']}ml")
                if metrics:
                    ctk.CTkLabel(ei, text=" • ".join(metrics),
                                font=ctk.CTkFont(size=11),
                                text_color=self.colors["info"]).pack(anchor="w", pady=(2, 0))

                if ev.get("notes"):
                    ctk.CTkLabel(ei, text=ev["notes"],
                                font=ctk.CTkFont(size=11),
                                text_color=self.colors["fg_secondary"],
                                wraplength=400, justify="left").pack(anchor="w", pady=(2, 0))

        # Show reminders
        if reminders:
            ctk.CTkLabel(scroll, text="Reminders",
                        font=ctk.CTkFont(size=14, weight="bold"),
                        text_color=self.colors["warning"]).pack(anchor="w", pady=(10, 3))

            for rem in reminders:
                rf = ctk.CTkFrame(scroll, fg_color=self.colors["bg_card"], corner_radius=8)
                rf.pack(fill="x", pady=3)
                ri = ctk.CTkFrame(rf, fg_color="transparent")
                ri.pack(fill="x", padx=12, pady=8)

                ctk.CTkLabel(ri, text=f"🔔 {rem.get('message', 'Reminder')}",
                            font=ctk.CTkFont(size=13),
                            text_color=self.colors["fg_primary"]).pack(side="left")

                rem_id = rem.get("id")
                if rem_id:
                    ctk.CTkButton(ri, text="✅ Done", width=70, height=24,
                                 font=ctk.CTkFont(size=10),
                                 fg_color=self.colors["success"],
                                 command=lambda rid=rem_id, d=dialog: self._complete_reminder(rid, d)
                                 ).pack(side="right")

        if not real_events and not reminders:
            ctk.CTkLabel(scroll, text="No events on this day.",
                        text_color=self.colors["fg_muted"]).pack(pady=20)

    def _complete_reminder(self, reminder_id, close_dialog=None):
        update_row("reminders", reminder_id, {
            "is_completed": 1,
            "completed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        })
        if close_dialog:
            close_dialog.destroy()
        self._render_calendar()

    def _prev_month(self):
        if self.current_month == 1:
            self.current_month = 12
            self.current_year -= 1
        else:
            self.current_month -= 1
        self._render_calendar()

    def _next_month(self):
        if self.current_month == 12:
            self.current_month = 1
            self.current_year += 1
        else:
            self.current_month += 1
        self._render_calendar()

    def _go_today(self):
        now = datetime.now()
        self.current_month = now.month
        self.current_year = now.year
        self._render_calendar()
