# FILE: growforge/ui/main_window.py
"""
GrowForge — Main application window with sidebar navigation.
"""

import customtkinter as ctk
from config import APP_NAME, APP_VERSION, APP_TAGLINE, COLORS
from database import get_setting, set_setting


class MainWindow:
    """Main application window with sidebar navigation and tab management."""

    def __init__(self, root: ctk.CTk):
        self.root = root
        self.root.title(f"{APP_NAME} — {APP_TAGLINE}")
        self.root.geometry("1280x800")
        self.root.minsize(1024, 650)

        # Theme
        self.theme = get_setting("theme", "dark")
        self.colors = COLORS[self.theme]
        ctk.set_appearance_mode("dark" if self.theme == "dark" else "light")
        ctk.set_default_color_theme("green")

        # Tabs registry
        self.tabs = {}
        self.current_tab = None
        self.tab_frames = {}

        self._build_layout()
        self._build_sidebar()
        self._load_tabs()
        self.show_tab("dashboard")

    def _build_layout(self):
        """Build the main two-pane layout."""
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar = ctk.CTkFrame(
            self.root, width=220, corner_radius=0,
            fg_color=self.colors["bg_sidebar"],
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        # Content area
        self.content = ctk.CTkFrame(
            self.root, corner_radius=0,
            fg_color=self.colors["bg_primary"],
        )
        self.content.grid(row=0, column=1, sticky="nsew")
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(0, weight=1)

    def _build_sidebar(self):
        """Build the sidebar with logo and nav buttons."""
        # Logo area
        logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo_frame.pack(fill="x", padx=15, pady=(20, 5))

        ctk.CTkLabel(
            logo_frame, text="🌿 GrowForge",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=self.colors["accent"],
        ).pack(anchor="w")

        ctk.CTkLabel(
            logo_frame, text=f"v{APP_VERSION}",
            font=ctk.CTkFont(size=11),
            text_color=self.colors["fg_muted"],
        ).pack(anchor="w")

        # Separator
        sep = ctk.CTkFrame(self.sidebar, height=1, fg_color=self.colors["border"])
        sep.pack(fill="x", padx=15, pady=(15, 10))

        # Navigation buttons
        self.nav_buttons = {}
        nav_items = [
            ("dashboard", "📊  Dashboard"),
            ("plants", "🌱  Plants"),
            ("environments", "🏠  Environments"),
            ("journal", "📓  Grow Journal"),
            ("calendar", "📅  Calendar"),
            ("cloning", "🧬  Cloning Station"),
            ("breeding", "🔬  Breeding Lab"),
            ("deficiency", "🩺  Deficiency Wizard"),
            ("tools", "🔧  Tools"),
            ("ai_assistant", "🤖  AI Assistant"),
            ("settings", "⚙️  Settings"),
        ]

        nav_scroll = ctk.CTkScrollableFrame(
            self.sidebar, fg_color="transparent",
            scrollbar_button_color=self.colors["bg_tertiary"],
        )
        nav_scroll.pack(fill="both", expand=True, padx=5, pady=5)

        for tab_id, label in nav_items:
            btn = ctk.CTkButton(
                nav_scroll,
                text=label,
                anchor="w",
                height=38,
                corner_radius=8,
                font=ctk.CTkFont(size=13),
                fg_color="transparent",
                text_color=self.colors["fg_secondary"],
                hover_color=self.colors["highlight"],
                command=lambda t=tab_id: self.show_tab(t),
            )
            btn.pack(fill="x", padx=5, pady=2)
            self.nav_buttons[tab_id] = btn

    def _load_tabs(self):
        """Import and initialize all tab modules."""
        from ui.dashboard import DashboardTab
        from ui.plants_tab import PlantsTab
        from ui.environments_tab import EnvironmentsTab
        from ui.journal_tab import JournalTab
        from ui.calendar_tab import CalendarTab
        from ui.cloning_tab import CloningTab
        from ui.breeding_tab import BreedingTab
        from ui.deficiency_wizard import DeficiencyWizardTab
        from ui.tools_tab import ToolsTab
        from ui.ai_assistant_tab import AIAssistantTab
        from ui.settings import SettingsTab

        self.tabs = {
            "dashboard": DashboardTab,
            "plants": PlantsTab,
            "environments": EnvironmentsTab,
            "journal": JournalTab,
            "calendar": CalendarTab,
            "cloning": CloningTab,
            "breeding": BreedingTab,
            "deficiency": DeficiencyWizardTab,
            "tools": ToolsTab,
            "ai_assistant": AIAssistantTab,
            "settings": SettingsTab,
        }

    def show_tab(self, tab_id: str):
        """Switch to the specified tab."""
        # Update nav button styles
        for tid, btn in self.nav_buttons.items():
            if tid == tab_id:
                btn.configure(
                    fg_color=self.colors["accent_dark"],
                    text_color=self.colors["fg_primary"],
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color=self.colors["fg_secondary"],
                )

        # Hide current tab
        for frame in self.tab_frames.values():
            frame.pack_forget()

        # Show or create the tab
        if tab_id not in self.tab_frames:
            frame = ctk.CTkFrame(self.content, fg_color=self.colors["bg_primary"], corner_radius=0)
            tab_class = self.tabs.get(tab_id)
            if tab_class:
                tab_class(frame, self)
            self.tab_frames[tab_id] = frame

        self.tab_frames[tab_id].pack(fill="both", expand=True)
        self.current_tab = tab_id

    def refresh_current_tab(self):
        """Rebuild the current tab to reflect data changes."""
        if self.current_tab and self.current_tab in self.tab_frames:
            old_frame = self.tab_frames.pop(self.current_tab)
            old_frame.destroy()
            self.show_tab(self.current_tab)

    def switch_theme(self, theme):
        """Switch between dark and light theme."""
        self.theme = theme
        self.colors = COLORS[theme]
        set_setting("theme", theme)
        ctk.set_appearance_mode("dark" if theme == "dark" else "light")
        # Rebuild all tabs
        for frame in self.tab_frames.values():
            frame.destroy()
        self.tab_frames.clear()
        self._build_layout()
        self._build_sidebar()
        self.show_tab(self.current_tab or "dashboard")
