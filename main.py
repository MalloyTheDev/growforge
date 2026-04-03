# FILE: growforge/main.py
"""
GrowForge — Main entry point and application launcher.
From Seed to Harvest, Clone to Cross: The Ultimate Local Desktop Cannabis Grow Assistant

Usage:
    python main.py

First launch will:
    1. Create the SQLite database
    2. Load the strain library
    3. Insert sample data
    4. Show welcome wizard
"""

import sys
import os

# Ensure growforge directory is on Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import customtkinter as ctk
from database import init_database, init_default_settings, get_setting, set_setting, insert_row, get_connection
from config import APP_NAME, APP_TAGLINE, APP_VERSION, COLORS, DATA_DIR
from knowledge_base import STRAIN_LIBRARY


def load_strain_library():
    """Load the prebuilt strain library, adding any missing strains."""
    conn = get_connection()
    existing = conn.execute("SELECT COUNT(*) FROM strains").fetchone()[0]
    conn.close()

    if existing >= len(STRAIN_LIBRARY):
        return  # already up to date

    print(f"  Syncing strain library ({existing} existing, {len(STRAIN_LIBRARY)} total)...")
    added = 0
    for strain in STRAIN_LIBRARY:
        try:
            insert_row("strains", strain)
            added += 1
        except Exception:
            pass  # strain already exists (UNIQUE constraint on name)
    if added:
        print(f"  ✅ Added {added} new strains (total: {existing + added})")

    # Normalize old strain_type values
    conn = get_connection()
    conn.execute("UPDATE strains SET strain_type='Hybrid' WHERE strain_type LIKE '%-dom Hybrid%'")
    conn.execute("UPDATE strains SET strain_type='Indica-dominant' WHERE strain_type='Indica-dom'")
    conn.execute("UPDATE strains SET is_autoflower=1 WHERE strain_type LIKE '%Auto%'")
    conn.execute("UPDATE strains SET strain_type='Indica' WHERE strain_type='Indica Auto'")
    conn.commit()
    conn.close()


def load_sample_data():
    """Load sample data on first launch."""
    sample_sql_path = DATA_DIR / "sample_data.sql"
    if not sample_sql_path.exists():
        print("  ⚠️ sample_data.sql not found, skipping sample data")
        return

    print("  Loading sample data...")
    conn = get_connection()
    with open(sample_sql_path, "r", encoding="utf-8") as f:
        sql = f.read()
    try:
        conn.executescript(sql)
        conn.commit()
        print("  ✅ Sample data loaded")
    except Exception as e:
        print(f"  ⚠️ Sample data error (may already exist): {e}")
    finally:
        conn.close()


def show_welcome_wizard(root):
    """Show first-launch welcome wizard."""
    wizard = ctk.CTkToplevel(root)
    wizard.title(f"Welcome to {APP_NAME}")
    wizard.geometry("550x480")
    wizard.transient(root)
    wizard.after(50, lambda: wizard.grab_set())
    wizard.resizable(False, False)

    colors = COLORS["dark"]

    # Center the wizard
    wizard.update_idletasks()
    x = (wizard.winfo_screenwidth() // 2) - 275
    y = (wizard.winfo_screenheight() // 2) - 240
    wizard.geometry(f"+{x}+{y}")

    frame = ctk.CTkFrame(wizard, fg_color=colors["bg_primary"], corner_radius=0)
    frame.pack(fill="both", expand=True)

    # Logo
    ctk.CTkLabel(
        frame, text="🌿",
        font=ctk.CTkFont(size=60),
    ).pack(pady=(30, 5))

    ctk.CTkLabel(
        frame, text=APP_NAME,
        font=ctk.CTkFont(size=32, weight="bold"),
        text_color=colors["accent"],
    ).pack()

    ctk.CTkLabel(
        frame, text=APP_TAGLINE,
        font=ctk.CTkFont(size=13),
        text_color=colors["fg_secondary"],
    ).pack(pady=(2, 20))

    ctk.CTkLabel(
        frame, text=f"Version {APP_VERSION} • 100% Local & Offline",
        font=ctk.CTkFont(size=11),
        text_color=colors["fg_muted"],
    ).pack()

    # Mode selection
    ctk.CTkLabel(
        frame, text="Choose your experience level:",
        font=ctk.CTkFont(size=15, weight="bold"),
        text_color=colors["fg_primary"],
    ).pack(pady=(25, 10))

    mode_var = ctk.StringVar(value="beginner")

    modes_frame = ctk.CTkFrame(frame, fg_color="transparent")
    modes_frame.pack()

    # Beginner card
    beg_frame = ctk.CTkFrame(modes_frame, fg_color=colors["bg_card"], corner_radius=12, width=220, height=100)
    beg_frame.pack(side="left", padx=10, pady=5)
    beg_frame.pack_propagate(False)

    ctk.CTkRadioButton(
        beg_frame, text="🌱 Beginner",
        variable=mode_var, value="beginner",
        font=ctk.CTkFont(size=14, weight="bold"),
    ).pack(anchor="w", padx=15, pady=(12, 2))
    ctk.CTkLabel(
        beg_frame, text="More guidance, tooltips,\nand step-by-step help",
        font=ctk.CTkFont(size=11), text_color=colors["fg_muted"],
    ).pack(anchor="w", padx=32)

    # Advanced card
    adv_frame = ctk.CTkFrame(modes_frame, fg_color=colors["bg_card"], corner_radius=12, width=220, height=100)
    adv_frame.pack(side="left", padx=10, pady=5)
    adv_frame.pack_propagate(False)

    ctk.CTkRadioButton(
        adv_frame, text="🔬 Advanced",
        variable=mode_var, value="advanced",
        font=ctk.CTkFont(size=14, weight="bold"),
    ).pack(anchor="w", padx=15, pady=(12, 2))
    ctk.CTkLabel(
        adv_frame, text="Full features, less hand-\nholding, breeding tools",
        font=ctk.CTkFont(size=11), text_color=colors["fg_muted"],
    ).pack(anchor="w", padx=32)

    def finish():
        set_setting("mode", mode_var.get())
        set_setting("first_launch", False)
        wizard.destroy()

    ctk.CTkButton(
        frame, text="🚀 Start Growing", width=200, height=44,
        font=ctk.CTkFont(size=16, weight="bold"),
        fg_color=colors["accent"],
        hover_color=colors["accent_hover"],
        corner_radius=10,
        command=finish,
    ).pack(pady=(25, 10))

    ctk.CTkLabel(
        frame, text="Sample data has been loaded so you can explore right away!",
        font=ctk.CTkFont(size=10),
        text_color=colors["fg_muted"],
    ).pack()

    wizard.wait_window()


def main():
    """Main application entry point."""
    print(f"\n🌿 {APP_NAME} v{APP_VERSION}")
    print(f"   {APP_TAGLINE}\n")

    # Initialize database
    print("Initializing database...")
    init_database()
    init_default_settings()

    # Load strain library
    load_strain_library()

    # Check first launch
    is_first = get_setting("first_launch", True)
    if is_first is True or is_first == "true":
        print("First launch detected — loading sample data...")
        load_sample_data()

    # Create main window
    print("Starting UI...")
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("green")

    root = ctk.CTk()
    root.title(f"{APP_NAME} — {APP_TAGLINE}")

    # Set window icon (cross-platform safe)
    try:
        root.iconbitmap(default="")
    except Exception:
        pass

    # Center on screen
    root.update_idletasks()
    w, h = 1280, 800
    x = (root.winfo_screenwidth() // 2) - (w // 2)
    y = (root.winfo_screenheight() // 2) - (h // 2)
    root.geometry(f"{w}x{h}+{x}+{y}")

    # Show welcome wizard on first launch
    if is_first is True or is_first == "true":
        root.after(200, lambda: show_welcome_wizard(root))

    # Build main window
    from ui.main_window import MainWindow
    app = MainWindow(root)

    # Start reminder engine
    from utils.reminders import ReminderEngine

    def on_reminders_due(reminders):
        """Callback when reminders fire — show notification in UI."""
        for r in reminders:
            msg = r.get('message', 'Reminder due!')
            print(f"  🔔 Reminder: {msg}")
            # Schedule UI notification on the main thread
            try:
                root.after(0, lambda m=msg: _show_reminder_popup(root, m))
            except Exception:
                pass

    def _show_reminder_popup(parent, message):
        """Show a small popup notification for a reminder."""
        popup = ctk.CTkToplevel(parent)
        popup.title("🔔 Reminder")
        popup.geometry("360x120")
        popup.attributes("-topmost", True)
        popup.resizable(False, False)
        # Position bottom-right
        popup.update_idletasks()
        sx = popup.winfo_screenwidth() - 380
        sy = popup.winfo_screenheight() - 180
        popup.geometry(f"+{sx}+{sy}")

        colors = COLORS["dark"]
        frame = ctk.CTkFrame(popup, fg_color=colors["bg_card"],
                             corner_radius=0)
        frame.pack(fill="both", expand=True)
        ctk.CTkLabel(frame, text="🔔 Reminder Due",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=colors["accent"]).pack(
                         padx=15, pady=(12, 4), anchor="w")
        ctk.CTkLabel(frame, text=message,
                     font=ctk.CTkFont(size=12),
                     text_color=colors["fg_primary"],
                     wraplength=320).pack(
                         padx=15, pady=(0, 8), anchor="w")
        ctk.CTkButton(frame, text="Dismiss", width=80, height=28,
                      fg_color=colors["accent"],
                      command=popup.destroy).pack(pady=(0, 10))
        # Auto-dismiss after 30 seconds
        popup.after(30000, popup.destroy)

    reminder_engine = ReminderEngine(callback=on_reminders_due)
    reminder_engine.start()

    print(f"✅ {APP_NAME} is running!\n")

    # Run
    root.mainloop()

    # Cleanup
    reminder_engine.stop()
    print(f"\n👋 {APP_NAME} closed. Happy growing!\n")


if __name__ == "__main__":
    main()
