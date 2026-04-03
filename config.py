# FILE: growforge/config.py
"""
GrowForge — Global configuration, constants, paths, and defaults.
"""

import os
import sys
from pathlib import Path

# ─── App Info ───────────────────────────────────────────────────────────────
APP_NAME = "GrowForge"
APP_VERSION = "1.0.0"
APP_TAGLINE = "From Seed to Harvest, Clone to Cross"

# ─── Paths ──────────────────────────────────────────────────────────────────
if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys.executable).parent
else:
    BASE_DIR = Path(__file__).parent

DATA_DIR = BASE_DIR / "data"
ASSETS_DIR = BASE_DIR / "assets"
ICONS_DIR = ASSETS_DIR / "icons"
DB_PATH = BASE_DIR / "growforge.db"
BACKUP_DIR = BASE_DIR / "backups"
EXPORT_DIR = BASE_DIR / "exports"
PHOTO_DIR = BASE_DIR / "photos"

# Create directories on import
for d in [DATA_DIR, ASSETS_DIR, ICONS_DIR, BACKUP_DIR, EXPORT_DIR, PHOTO_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ─── Database ───────────────────────────────────────────────────────────────
DB_NAME = str(DB_PATH)

# ─── UI Theme Colors ───────────────────────────────────────────────────────
COLORS = {
    "dark": {
        "bg_primary": "#0f1a0f",
        "bg_secondary": "#1a2e1a",
        "bg_tertiary": "#243524",
        "bg_card": "#1e2d1e",
        "bg_sidebar": "#0d160d",
        "bg_input": "#2a3d2a",
        "fg_primary": "#e8f5e8",
        "fg_secondary": "#a8c8a8",
        "fg_muted": "#6a8a6a",
        "accent": "#4caf50",
        "accent_hover": "#66bb6a",
        "accent_dark": "#2e7d32",
        "success": "#4caf50",
        "warning": "#ff9800",
        "error": "#f44336",
        "info": "#29b6f6",
        "border": "#2a3d2a",
        "highlight": "#3a5c3a",
    },
    "light": {
        "bg_primary": "#f5f9f5",
        "bg_secondary": "#e8f0e8",
        "bg_tertiary": "#dce8dc",
        "bg_card": "#ffffff",
        "bg_sidebar": "#e0ede0",
        "bg_input": "#ffffff",
        "fg_primary": "#1a2e1a",
        "fg_secondary": "#3a5c3a",
        "fg_muted": "#6a8a6a",
        "accent": "#2e7d32",
        "accent_hover": "#388e3c",
        "accent_dark": "#1b5e20",
        "success": "#2e7d32",
        "warning": "#e65100",
        "error": "#c62828",
        "info": "#0277bd",
        "border": "#c8d8c8",
        "highlight": "#c8e6c9",
    },
}

# ─── Growth Stages ──────────────────────────────────────────────────────────
STAGES = [
    "Germination",
    "Seedling",
    "Vegetative",
    "Flowering",
    "Flushing",
    "Drying",
    "Curing",
    "Harvested",
]

CLONE_STAGES = [
    "Cut Taken",
    "Rooting",
    "Rooted",
    "Transplanted",
    "Vegetative",
]

# ─── Event Types ────────────────────────────────────────────────────────────
EVENT_TYPES = [
    "Watering",
    "Feeding",
    "Training (LST)",
    "Training (Topping)",
    "Training (FIM)",
    "Training (SCROG)",
    "Training (Supercropping)",
    "Training (Defoliation)",
    "Pruning",
    "Transplant",
    "Light Change",
    "Stage Change",
    "Photo",
    "Observation",
    "pH Reading",
    "EC/PPM Reading",
    "Pest Treatment",
    "Issue Detected",
    "Clone Taken",
    "Pollination",
    "Harvest",
    "Other",
]

# ─── Growing Mediums ────────────────────────────────────────────────────────
MEDIUMS = [
    "Soil (Organic)",
    "Soil (Amended)",
    "Coco Coir",
    "Coco/Perlite Mix",
    "Perlite",
    "Rockwool",
    "Clay Pebbles (Hydroton)",
    "DWC (Deep Water Culture)",
    "NFT (Nutrient Film)",
    "Ebb & Flow",
    "Aeroponics",
    "Living Soil",
    "Super Soil",
]

# ─── Light Types ────────────────────────────────────────────────────────────
LIGHT_TYPES = [
    "LED (Full Spectrum)",
    "LED (Quantum Board)",
    "LED (COB)",
    "LED (Bar Style)",
    "HPS (High Pressure Sodium)",
    "MH (Metal Halide)",
    "CMH (Ceramic Metal Halide)",
    "CFL (Compact Fluorescent)",
    "T5 Fluorescent",
    "Sunlight (Outdoor)",
]

# ─── Plant Types ────────────────────────────────────────────────────────────
PLANT_TYPES = ["Photoperiod", "Autoflower"]
STRAIN_TYPES = ["Indica", "Sativa", "Hybrid", "Indica-dominant", "Sativa-dominant"]
GENETICS_TYPES = ["Regular", "Feminized", "Autoflower", "Clone", "Seed (from cross)"]

# ─── Stage Colors ──────────────────────────────────────────────────────────
STAGE_COLORS = {
    "Germination": "#9c27b0",
    "Seedling": "#66bb6a",
    "Vegetative": "#29b6f6",
    "Flowering": "#ffa726",
    "Flushing": "#ef5350",
    "Drying": "#8d6e63",
    "Curing": "#78909c",
    "Harvested": "#4caf50",
}

# ─── Defaults ───────────────────────────────────────────────────────────────
DEFAULT_SETTINGS = {
    "theme": "dark",
    "mode": "beginner",
    "reminder_check_interval": 60,  # seconds
    "default_water_interval_days": 2,
    "default_feed_interval_days": 4,
    "temp_unit": "C",  # C or F
    "first_launch": True,
}

# ─── VPD Table Boundaries ──────────────────────────────────────────────────
# Canonical source is knowledge_base.VPD_ZONES

# ─── Phenotype Scoring Categories ──────────────────────────────────────────
PHENO_SCORE_CATEGORIES = [
    "Vigor",
    "Structure",
    "Yield Potential",
    "Terpene Profile",
    "Resin Production",
    "Pest Resistance",
    "Mold Resistance",
    "Bag Appeal",
    "Potency",
    "Flavor",
]

# ─── Rooting Methods ───────────────────────────────────────────────────────
ROOTING_METHODS = [
    "Rooting Gel + Rapid Rooter",
    "Rooting Powder + Rockwool",
    "Rooting Gel + Perlite",
    "Clonex + Aeroponic Cloner",
    "Water Cloning (no hormone)",
    "Aloe Vera Gel (organic)",
    "Honey (organic)",
]
