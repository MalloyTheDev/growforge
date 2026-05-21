#pragma once

#include <QString>
#include <QStringList>
#include <QMap>
#include <QColor>

// GrowForge — Global configuration, constants, and defaults.
// Ported from config.py, with a "command center" dark palette derived from
// the GrowForge.html design tokens (oklch values approximated to hex).
namespace Config {

inline const QString APP_NAME = "GrowForge";
inline const QString APP_VERSION = "1.0.0";
inline const QString APP_TAGLINE = "From Seed to Harvest, Clone to Cross";

// ─── Palette ────────────────────────────────────────────────────────────────
struct Palette {
    QString bg0;          // page background (darkest)
    QString bg1;          // card / panel surface
    QString bg2;          // input / inset surface
    QString bg3;          // raised surface
    QString bg4;          // hover / pressed
    QString sidebar;      // sidebar gradient top
    QString sidebarEnd;   // sidebar gradient bottom
    QString line;         // default border
    QString lineStrong;   // strong border
    QString lineSoft;     // subtle divider
    QString fg0;          // primary text
    QString fg1;          // secondary text
    QString fg2;          // muted text
    QString fg3;          // dim text
    QString fg4;          // faint text
    QString accent;       // brand accent
    QString accent2;      // darker accent
    QString accentSoft;   // translucent accent fill (rgba)
    QString accentLine;   // accent border (rgba)
    QString sensor;       // blue (cool)
    QString warn;         // amber
    QString crit;         // red
    QString violet;       // violet
    QString success;
    QString info;
};

// Command-center dark theme (primary look).
inline const Palette DARK = {
    /*bg0*/        "#07090a",
    /*bg1*/        "#0c1010",
    /*bg2*/        "#111614",
    /*bg3*/        "#161c19",
    /*bg4*/        "#1c2320",
    /*sidebar*/    "#0a0d0c",
    /*sidebarEnd*/ "#07090a",
    /*line*/       "#1f2723",
    /*lineStrong*/ "#2a322d",
    /*lineSoft*/   "#181d1a",
    /*fg0*/        "#eaeeea",
    /*fg1*/        "#c2c8c3",
    /*fg2*/        "#8a918c",
    /*fg3*/        "#5b625d",
    /*fg4*/        "#3a403c",
    /*accent*/     "#82b58f",
    /*accent2*/    "#5e9d6f",
    /*accentSoft*/ "rgba(130,181,143,0.16)",
    /*accentLine*/ "rgba(130,181,143,0.42)",
    /*sensor*/     "#74a9cf",
    /*warn*/       "#d9a441",
    /*crit*/       "#d65f4a",
    /*violet*/     "#b07cc9",
    /*success*/    "#82b58f",
    /*info*/       "#74a9cf",
};

// Light theme (kept close to config.py light scheme, command-center flavored).
inline const Palette LIGHT = {
    /*bg0*/        "#f3f6f3",
    /*bg1*/        "#ffffff",
    /*bg2*/        "#eef3ee",
    /*bg3*/        "#e4ece4",
    /*bg4*/        "#d8e4d8",
    /*sidebar*/    "#e7efe7",
    /*sidebarEnd*/ "#dde8dd",
    /*line*/       "#c8d8c8",
    /*lineStrong*/ "#b3c7b3",
    /*lineSoft*/   "#dce8dc",
    /*fg0*/        "#142016",
    /*fg1*/        "#33503a",
    /*fg2*/        "#5a715f",
    /*fg3*/        "#7d927f",
    /*fg4*/        "#9fb0a0",
    /*accent*/     "#2e7d32",
    /*accent2*/    "#1b5e20",
    /*accentSoft*/ "rgba(46,125,50,0.14)",
    /*accentLine*/ "rgba(46,125,50,0.40)",
    /*sensor*/     "#0277bd",
    /*warn*/       "#e65100",
    /*crit*/       "#c62828",
    /*violet*/     "#7b3fa0",
    /*success*/    "#2e7d32",
    /*info*/       "#0277bd",
};

inline const Palette &palette(const QString &theme) {
    return theme == "light" ? LIGHT : DARK;
}

// ─── Growth Stages ────────────────────────────────────────────────────────
inline const QStringList STAGES = {
    "Germination", "Seedling", "Vegetative", "Flowering",
    "Flushing", "Drying", "Curing", "Harvested",
};

inline const QStringList CLONE_STAGES = {
    "Cut Taken", "Rooting", "Rooted", "Transplanted", "Vegetative",
};

// ─── Event Types ────────────────────────────────────────────────────────────
inline const QStringList EVENT_TYPES = {
    "Watering", "Feeding", "Training (LST)", "Training (Topping)",
    "Training (FIM)", "Training (SCROG)", "Training (Supercropping)",
    "Training (Defoliation)", "Pruning", "Transplant", "Light Change",
    "Stage Change", "Photo", "Observation", "pH Reading", "EC/PPM Reading",
    "Pest Treatment", "Issue Detected", "Clone Taken", "Pollination",
    "Harvest", "Other",
};

// ─── Growing Mediums ────────────────────────────────────────────────────────
inline const QStringList MEDIUMS = {
    "Soil (Organic)", "Soil (Amended)", "Coco Coir", "Coco/Perlite Mix",
    "Perlite", "Rockwool", "Clay Pebbles (Hydroton)", "DWC (Deep Water Culture)",
    "NFT (Nutrient Film)", "Ebb & Flow", "Aeroponics", "Living Soil", "Super Soil",
};

// ─── Light Types ────────────────────────────────────────────────────────────
inline const QStringList LIGHT_TYPES = {
    "LED (Full Spectrum)", "LED (Quantum Board)", "LED (COB)", "LED (Bar Style)",
    "HPS (High Pressure Sodium)", "MH (Metal Halide)", "CMH (Ceramic Metal Halide)",
    "CFL (Compact Fluorescent)", "T5 Fluorescent", "Sunlight (Outdoor)",
};

// ─── Plant / Strain / Genetics types ────────────────────────────────────────
inline const QStringList PLANT_TYPES = {"Photoperiod", "Autoflower"};
inline const QStringList STRAIN_TYPES = {
    "Indica", "Sativa", "Hybrid", "Indica-dominant", "Sativa-dominant",
};
inline const QStringList GENETICS_TYPES = {
    "Regular", "Feminized", "Autoflower", "Clone", "Seed (from cross)",
};

// ─── Stage Colors ──────────────────────────────────────────────────────────
inline QString stageColor(const QString &stage) {
    static const QMap<QString, QString> m = {
        {"Germination", "#b07cc9"},
        {"Seedling",    "#7cc08a"},
        {"Vegetative",  "#74a9cf"},
        {"Flowering",   "#d9a441"},
        {"Flushing",    "#d65f4a"},
        {"Drying",      "#a98a78"},
        {"Curing",      "#90a0aa"},
        {"Harvested",   "#82b58f"},
    };
    return m.value(stage, "#8a918c");
}

// ─── Phenotype Scoring Categories ──────────────────────────────────────────
inline const QStringList PHENO_SCORE_CATEGORIES = {
    "Vigor", "Structure", "Yield Potential", "Terpene Profile",
    "Resin Production", "Pest Resistance", "Mold Resistance",
    "Bag Appeal", "Potency", "Flavor",
};

// ─── Growing Hub Stage Groups ──────────────────────────────────────────────
inline const QMap<QString, QStringList> STAGE_GROUPS = {
    {"seed",   {"Germination", "Seedling"}},
    {"veg",    {"Vegetative"}},
    {"flower", {"Flowering", "Flushing"}},
};

// ─── Rooting Methods ───────────────────────────────────────────────────────
inline const QStringList ROOTING_METHODS = {
    "Rooting Gel + Rapid Rooter", "Rooting Powder + Rockwool",
    "Rooting Gel + Perlite", "Clonex + Aeroponic Cloner",
    "Water Cloning (no hormone)", "Aloe Vera Gel (organic)", "Honey (organic)",
};

// ─── Default settings ────────────────────────────────────────────────────────
struct DefaultSetting { const char *key; const char *value; };
inline const QList<DefaultSetting> DEFAULT_SETTINGS = {
    {"theme", "dark"},
    {"mode", "beginner"},
    {"reminder_check_interval", "60"},
    {"default_water_interval_days", "2"},
    {"default_feed_interval_days", "4"},
    {"temp_unit", "C"},
    {"first_launch", "true"},
};

} // namespace Config
