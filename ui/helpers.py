# FILE: growforge/ui/helpers.py
"""
GrowForge — Shared UI helpers: toast notifications, form validation, reusable widgets.
"""

import customtkinter as ctk
from datetime import datetime


def show_toast(parent, message, toast_type="success", duration=3000):
    """Show a temporary toast notification at the top of a parent widget.

    Args:
        parent: The parent widget to attach the toast to.
        message: Text to display.
        toast_type: "success", "error", "warning", or "info".
        duration: Auto-dismiss time in ms (0 = no auto-dismiss).
    """
    colors = {
        "success": ("#2e7d32", "#e8f5e9"),
        "error": ("#c62828", "#ffebee"),
        "warning": ("#e65100", "#fff3e0"),
        "info": ("#0277bd", "#e1f5fe"),
    }
    icons = {"success": "✅", "error": "❌", "warning": "⚠️", "info": "ℹ️"}

    fg, bg = colors.get(toast_type, colors["info"])

    toast = ctk.CTkFrame(parent, fg_color=bg, corner_radius=8, height=36)
    toast.pack(fill="x", padx=25, pady=(5, 2))
    toast.pack_propagate(False)

    icon = icons.get(toast_type, "ℹ️")
    ctk.CTkLabel(
        toast, text=f"{icon}  {message}",
        font=ctk.CTkFont(size=12, weight="bold"),
        text_color=fg,
    ).pack(side="left", padx=12, pady=6)

    if duration > 0:
        toast.after(duration, toast.destroy)

    return toast


def validate_not_empty(value, field_name):
    """Return error message if value is empty, else None."""
    if not value or not value.strip():
        return f"{field_name} cannot be empty."
    return None


def validate_date(value, field_name="Date"):
    """Return error message if value is not a valid YYYY-MM-DD date, else None."""
    if not value or not value.strip():
        return None  # empty is ok, not required
    try:
        datetime.strptime(value.strip(), "%Y-%m-%d")
        return None
    except ValueError:
        return f"{field_name} must be in YYYY-MM-DD format."


def validate_positive_number(value, field_name, allow_zero=True, allow_float=True):
    """Return error message if value is not a valid positive number, else None."""
    if not value or not value.strip():
        return None  # empty is ok
    try:
        num = float(value) if allow_float else int(value)
        if num < 0:
            return f"{field_name} cannot be negative."
        if not allow_zero and num == 0:
            return f"{field_name} must be greater than zero."
        return None
    except ValueError:
        kind = "number" if allow_float else "whole number"
        return f"{field_name} must be a valid {kind}."


def safe_int(value, default=0):
    """Parse int safely, return default on failure."""
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return default


def safe_float(value, default=0.0):
    """Parse float safely, return default on failure."""
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def extract_id_from_option(option_str):
    """Extract numeric ID from strings like 'Plant Name (#42)'. Returns None on failure."""
    if not option_str or "(#" not in option_str:
        return None
    try:
        return int(option_str.split("#")[1].rstrip(")"))
    except (IndexError, ValueError):
        return None


def show_validation_error(parent, message, colors):
    """Show a red error label inside a dialog. Returns the label for later removal."""
    err = ctk.CTkLabel(
        parent, text=f"⚠️ {message}",
        font=ctk.CTkFont(size=12),
        text_color=colors.get("error", "#f44336"),
    )
    err.pack(anchor="w", padx=5, pady=(2, 0))
    return err
