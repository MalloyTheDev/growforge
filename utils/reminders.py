# FILE: growforge/utils/reminders.py
"""
GrowForge — Background reminder checker using schedule + threading.
"""

import threading
import time
from datetime import datetime, timedelta
import schedule


class ReminderEngine:
    """Background reminder checking engine."""

    def __init__(self, callback=None):
        self._running = False
        self._thread = None
        self.callback = callback  # Function to call when reminders are due

    def start(self):
        """Start the background reminder checker."""
        if self._running:
            return
        self._running = True
        schedule.every(60).seconds.do(self._check_reminders)
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def stop(self):
        """Stop the background checker."""
        self._running = False
        schedule.clear()

    def _run_loop(self):
        while self._running:
            schedule.run_pending()
            time.sleep(10)

    def _check_reminders(self):
        """Check for due reminders and trigger callback."""
        if not self.callback:
            return
        try:
            from database import get_due_reminders
            due = get_due_reminders()
            if due:
                self.callback(due)
        except Exception as e:
            print(f"Reminder check error: {e}")

    def create_reminder(self, plant_id, reminder_type, due_date, message,
                        recurring=False, recurrence_days=0):
        """Create a new reminder in the database."""
        from database import insert_row
        data = {
            "plant_id": plant_id,
            "reminder_type": reminder_type,
            "due_date": due_date,
            "message": message,
            "is_recurring": 1 if recurring else 0,
            "recurrence_days": recurrence_days,
            "is_completed": 0,
        }
        return insert_row("reminders", data)

    def complete_reminder(self, reminder_id, reschedule=True):
        """Mark a reminder as completed, optionally reschedule if recurring."""
        from database import update_row, get_row
        reminder = get_row("reminders", reminder_id)
        if not reminder:
            return

        update_row("reminders", reminder_id, {
            "is_completed": 1,
            "completed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        })

        # Reschedule if recurring
        if reschedule and reminder.get("is_recurring") and reminder.get("recurrence_days", 0) > 0:
            next_due = (datetime.now() + timedelta(days=reminder["recurrence_days"]))
            self.create_reminder(
                plant_id=reminder.get("plant_id"),
                reminder_type=reminder["reminder_type"],
                due_date=next_due.strftime("%Y-%m-%d %H:%M:%S"),
                message=reminder.get("message", ""),
                recurring=True,
                recurrence_days=reminder["recurrence_days"],
            )


def create_default_reminders(plant_id, plant_name, stage):
    """Create common reminders based on plant stage."""
    from database import insert_row
    now = datetime.now()

    reminders = []
    if stage in ["Seedling", "Vegetative", "Flowering"]:
        # Watering reminder every 2 days
        reminders.append({
            "plant_id": plant_id,
            "reminder_type": "Watering",
            "due_date": (now + timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S"),
            "message": f"Water {plant_name}",
            "is_recurring": 1,
            "recurrence_days": 2,
            "is_completed": 0,
        })
        # Feeding reminder every 4 days
        reminders.append({
            "plant_id": plant_id,
            "reminder_type": "Feeding",
            "due_date": (now + timedelta(days=4)).strftime("%Y-%m-%d %H:%M:%S"),
            "message": f"Feed {plant_name}",
            "is_recurring": 1,
            "recurrence_days": 4,
            "is_completed": 0,
        })

    if stage == "Vegetative":
        reminders.append({
            "plant_id": plant_id,
            "reminder_type": "Check",
            "due_date": (now + timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S"),
            "message": f"Check {plant_name} for sex / preflowers",
            "is_recurring": 0,
            "recurrence_days": 0,
            "is_completed": 0,
        })

    for r in reminders:
        insert_row("reminders", r)
