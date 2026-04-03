# FILE: growforge/knowledge_base.py
"""
GrowForge — Comprehensive cannabis cultivation knowledge base.
Contains stage data, nutrient deficiency tables, VPD charts,
cloning/breeding guides, strain library, training techniques,
pest identification, glossary, symptom decision trees,
rule weight system, feedback schema, and self-coding templates.

This module is the ground-truth data source for GrowForge AI.
All rules, thresholds, and patterns are defined here so the AI
engine can reference them. The adaptive learning system can
modify rule_weights and generate new rules into learned_rules.py.
"""

import math

# ════════════════════════════════════════════════════════════════════════════
#  RULE WEIGHTS — Confidence modifiers that the AI adjusts via feedback.
#  Each weight starts at 1.0 (neutral). Values >1 = higher confidence in
#  that rule, <1 = lower. The self-coding engine updates these.
# ════════════════════════════════════════════════════════════════════════════

rule_weights = {
    "nitrogen_def": 1.0, "phosphorus_def": 1.0, "potassium_def": 1.0,
    "calcium_def": 1.0, "magnesium_def": 1.0, "iron_def": 1.0,
    "zinc_def": 1.0, "manganese_def": 1.0, "sulfur_def": 1.0, "boron_def": 1.0,
    "spider_mites": 1.0, "fungus_gnats": 1.0, "thrips": 1.0,
    "aphids": 1.0, "powdery_mildew": 1.0, "bud_rot": 1.0, "root_rot": 1.0,
    "ph_lockout": 1.0, "vpd_alert": 1.0, "temp_alert": 1.0, "rh_alert": 1.0,
    "overwater": 1.0, "underwater": 1.0, "nute_burn": 1.0,
    "stage_transition": 1.0, "harvest_timing": 1.0, "flush_timing": 1.0,
    "training_rec": 1.0, "auto_caution": 1.0,
    "clone_success": 1.0, "clone_timeline": 1.0,
    "breeding_advice": 1.0, "pheno_scoring": 1.0,
}

# ════════════════════════════════════════════════════════════════════════════
#  FEEDBACK HISTORY SCHEMA
# ════════════════════════════════════════════════════════════════════════════

FEEDBACK_SCHEMA = {
    "ai_feedback_sql": """CREATE TABLE IF NOT EXISTS ai_feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        plant_id INTEGER, timestamp TEXT DEFAULT (datetime('now')),
        ai_suggestion TEXT NOT NULL, user_correction TEXT DEFAULT '',
        rating INTEGER DEFAULT 0, issue_type TEXT DEFAULT '',
        outcome_details TEXT DEFAULT '', rule_id TEXT DEFAULT '',
        was_correct INTEGER DEFAULT -1)""",
    "ai_learned_rules_sql": """CREATE TABLE IF NOT EXISTS ai_learned_rules (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        rule_name TEXT UNIQUE NOT NULL, rule_code TEXT NOT NULL,
        source_feedback_ids TEXT DEFAULT '', confidence REAL DEFAULT 0.8,
        times_applied INTEGER DEFAULT 0, times_correct INTEGER DEFAULT 0,
        created_at TEXT DEFAULT (datetime('now')),
        updated_at TEXT DEFAULT (datetime('now')))""",
    "ai_rule_weights_sql": """CREATE TABLE IF NOT EXISTS ai_rule_weights (
        rule_id TEXT PRIMARY KEY, weight REAL DEFAULT 1.0,
        adjustments INTEGER DEFAULT 0,
        last_adjusted TEXT DEFAULT (datetime('now')))""",
}

# ════════════════════════════════════════════════════════════════════════════
#  SELF-CODING TEMPLATES — Safe templates the AI uses to write new rules
# ════════════════════════════════════════════════════════════════════════════

RULE_TEMPLATES = {
    "symptom_rule": '''def rule_{name}(symptoms, leaf_loc, medium, ph, stage):
    """Auto-generated: {description} | From feedback #{feedback_ids} | {timestamp}"""
    score = 0.0
    {conditions}
    return ("{diagnosis}", round(score * {confidence}, 2))
''',
    "stage_override": '''def rule_{name}(stage, day_count, plant_type, events):
    """Auto-generated stage rule: {description} | {timestamp}"""
    {conditions}
    return {result}
''',
    "clone_predictor": '''def rule_{name}(method, medium, temp, humidity):
    """Auto-generated clone predictor: {description} | {timestamp}"""
    chance = 0.75
    {adjustments}
    return round(min(0.99, max(0.1, chance)), 2)
''',
    "custom_alert": '''def rule_{name}(plant, events, env):
    """Auto-generated alert: {description} | {timestamp}"""
    alerts = []
    {conditions}
    return alerts
''',
}

# Lines in generated code must match one of these patterns (safety filter)
import re as _re
SAFE_CODE_PATTERNS = [
    _re.compile(r'^def rule_\w+\('),
    _re.compile(r'^\s+"""'),
    _re.compile(r'^\s+score\s*[+\-\*]?='),
    _re.compile(r'^\s+chance\s*[+\-\*]?='),
    _re.compile(r'^\s+if\s+'),
    _re.compile(r'^\s+elif\s+'),
    _re.compile(r'^\s+else\s*:'),
    _re.compile(r'^\s+return\s+'),
    _re.compile(r'^\s+alerts\.append'),
    _re.compile(r'^\s+#'),
    _re.compile(r'^\s+\w+\s*=\s*'),
    _re.compile(r'^\s+for\s+\w+\s+in\s+'),
    _re.compile(r'^\s*$'),
]

# Patterns that should NEVER appear in generated code (security blocklist)
BLOCKED_CODE_PATTERNS = [
    _re.compile(r'import\s'),        # no imports
    _re.compile(r'__\w+__'),         # no dunder access
    _re.compile(r'exec\s*\('),       # no exec
    _re.compile(r'eval\s*\('),       # no eval
    _re.compile(r'compile\s*\('),    # no compile
    _re.compile(r'open\s*\('),       # no file access
    _re.compile(r'os\.'),            # no os module
    _re.compile(r'sys\.'),           # no sys module
    _re.compile(r'subprocess'),      # no subprocess
    _re.compile(r'globals\s*\('),    # no globals access
    _re.compile(r'locals\s*\('),     # no locals access
    _re.compile(r'getattr\s*\('),    # no dynamic attr access
    _re.compile(r'setattr\s*\('),    # no dynamic attr setting
    _re.compile(r'delattr\s*\('),    # no dynamic attr deletion
    _re.compile(r'lambda\s'),        # no lambdas
    _re.compile(r'class\s'),         # no class definitions
]

def validate_generated_code(code_str):
    """Return True only if every line matches a safe pattern and no
    line matches a blocked pattern."""
    for line in code_str.strip().splitlines():
        # Check blocklist first
        stripped = line.strip()
        if stripped and not stripped.startswith('#') and not stripped.startswith('"""'):
            for blocked in BLOCKED_CODE_PATTERNS:
                if blocked.search(stripped):
                    return False
        # Check allowlist
        if not any(p.match(line) for p in SAFE_CODE_PATTERNS):
            return False
    return True

# ════════════════════════════════════════════════════════════════════════════
#  VPD ZONES — Stage-specific target ranges (kPa)
# ════════════════════════════════════════════════════════════════════════════

VPD_ZONES = {
    "danger_low": (0.0, 0.4),
    "early_veg": (0.4, 0.8),
    "late_veg": (0.8, 1.0),
    "early_flower": (1.0, 1.2),
    "mid_flower": (1.2, 1.4),
    "late_flower": (1.3, 1.6),
    "danger_high": (1.6, 3.0),
}

# ════════════════════════════════════════════════════════════════════════════
#  VPD HELPERS
# ════════════════════════════════════════════════════════════════════════════

def calc_vpd(temp_c, rh_pct, leaf_offset=2.0):
    lt = temp_c - leaf_offset
    svp_l = 0.6108 * math.exp((17.27 * lt) / (lt + 237.3))
    svp_a = 0.6108 * math.exp((17.27 * temp_c) / (temp_c + 237.3))
    return round(max(0.0, svp_l - svp_a * (rh_pct / 100.0)), 3)

def ideal_rh_for_vpd(temp_c, target_vpd, leaf_offset=2.0):
    lt = temp_c - leaf_offset
    svp_l = 0.6108 * math.exp((17.27 * lt) / (lt + 237.3))
    svp_a = 0.6108 * math.exp((17.27 * temp_c) / (temp_c + 237.3))
    rh = ((svp_l - target_vpd) / svp_a) * 100
    return round(max(0, min(100, rh)), 1)

# ════════════════════════════════════════════════════════════════════════════
#  GROWTH STAGE DEFINITIONS
# ════════════════════════════════════════════════════════════════════════════

STAGE_GUIDE = {
    "Germination": {
        "duration": "2-10 days", "duration_days": (2, 10),
        "temp_range": (20, 25), "rh_range": (70, 90), "vpd_target": (0.4, 0.6),
        "light_hours_photo": "Dark or very dim", "light_hours_auto": "Dark or very dim",
        "ppfd": (0, 50), "next_stage": "Seedling",
        "nutrient_needs": "None", "watering": "Mist only",
        "transition_signs": ["Taproot 0.5-1 inch", "Seed cracked", "Cotyledons visible"],
        "description": "Soak seeds 12-24h then paper towel method or direct sow. Keep warm, dark, humid.",
        "checklist": ["Soak 12-24h pH 6.0-6.5", "Moist paper towel 20-25C", "Check 2x daily", "Plant taproot down 0.5in deep"],
        "common_issues": [
            ("Seed won't crack", "Scuff with sandpaper, longer soak, check temp"),
            ("Damping off", "Too wet, improve airflow"), ("Slow germ", "Check temp consistency")],
    },
    "Seedling": {
        "duration": "1-3 weeks", "duration_days": (7, 21),
        "temp_range": (20, 25), "rh_range": (60, 70), "vpd_target": (0.4, 0.8),
        "light_hours_photo": "18/6", "light_hours_auto": "18/6 or 20/4",
        "ppfd": (200, 400), "next_stage": "Vegetative",
        "nutrient_needs": "None week 1, then 1/4 strength EC 0.4-0.6",
        "watering": "Small circles, 50-100ml, let top dry slightly",
        "transition_signs": ["3-4 sets true leaves", "Sturdy stem", "Roots visible at pot bottom"],
        "description": "First true leaves. Very fragile. Humidity dome recommended. Light feed after 2nd true leaf set.",
        "checklist": ["60-70% RH dome", "200-400 PPFD 24-30in", "No nutes week 1", "1/4 strength week 2+", "Watch for stretch"],
        "common_issues": [
            ("Stretching", "Light too far/dim — lower or intensify"),
            ("Yellow cotyledons", "Normal — they're food reserves"),
            ("Damping off", "Reduce moisture, increase airflow")],
    },
    "Vegetative": {
        "duration": "1-15+ wk photo, 3-5 wk auto", "duration_days": (21, 105),
        "auto_duration_days": (14, 35),
        "temp_range": (22, 28), "rh_range": (40, 70), "vpd_target": (0.8, 1.2),
        "light_hours_photo": "18/6 or 24/0", "light_hours_auto": "18/6 or 20/4",
        "ppfd": (400, 600), "next_stage": "Flowering",
        "nutrient_needs": "Full veg nutes, high N ratio 3-1-2, EC 1.0-1.6",
        "watering": "Water to 10-20% runoff, let dry between",
        "transition_signs": ["Desired height reached", "Canopy full", "Preflowers visible", "SCROG 60-70% full"],
        "description": "Rapid growth. Increase nutes gradually. Train after 4-5 nodes. Transplant as needed. Flip decision point.",
        "checklist": ["400-600 PPFD", "Full veg nutes high N", "pH 6.0-6.8 soil / 5.5-6.5 hydro",
                      "LST/top after node 4-5", "Transplant when rootbound", "Check sex if regs", "Oscillating fan on stems"],
        "common_issues": [
            ("N deficiency lower yellowing", "Increase N, check pH"),
            ("Overwatering droopy dark", "Let dry, lift test"),
            ("Light stress bleach/taco", "Raise light, check PPFD<700"),
            ("Root bound slow growth", "Transplant up a size")],
    },
    "Flowering": {
        "duration": "7-14 weeks", "duration_days": (49, 98),
        "temp_range": (18, 26), "rh_range": (40, 50), "vpd_target": (1.0, 1.5),
        "light_hours_photo": "12/12", "light_hours_auto": "18/6 or 20/4",
        "ppfd": (600, 900), "next_stage": "Flushing",
        "nutrient_needs": "Bloom nutes 1-3-2, PK booster wk4-6, Cal-Mag throughout",
        "watering": "To runoff, plants drink more",
        "sub_stages": {
            "Early Flower (wk 1-3)": {"vpd": (1.0, 1.2), "rh": (45, 55), "notes": "Stretch phase. Transition nutes. Remove males. Last training."},
            "Mid Flower (wk 4-6)": {"vpd": (1.2, 1.4), "rh": (40, 50), "notes": "Bud formation. PK boost. Support branches."},
            "Late Flower (wk 7+)": {"vpd": (1.3, 1.5), "rh": (35, 45), "notes": "Ripening. Check trichomes. Begin flush 1-2wk before harvest."},
        },
        "transition_signs": ["Trichomes clear→cloudy", "60-80% pistils brown", "Calyxes swollen", "Growth slowed"],
        "description": "12/12 triggers flowering for photo. Increase P-K, reduce N. Monitor trichomes from wk6+.",
        "checklist": ["12/12 zero light leaks", "Bloom nutes high PK", "Remove males 24h", "RH 40-50%",
                      "Support branches", "Stop training wk3", "Check trichomes wk6+", "Flush 7-14d before harvest"],
        "common_issues": [
            ("Light leaks herming", "Seal ALL leaks, check during dark"),
            ("Bud rot gray mold", "Cut 2in below, RH<45%, airflow"),
            ("K def burnt edges", "Increase K, check pH"),
            ("Foxtailing", "Heat/light stress — raise light, cool down")],
    },
    "Flushing": {
        "duration": "7-14 days", "duration_days": (7, 14),
        "temp_range": (18, 24), "rh_range": (35, 45), "vpd_target": (1.3, 1.5),
        "light_hours_photo": "12/12", "light_hours_auto": "18/6",
        "ppfd": (400, 600), "next_stage": "Drying",
        "nutrient_needs": "NONE — plain pH'd water only",
        "watering": "To 20% runoff each time",
        "transition_signs": ["80-90% cloudy + 10-20% amber trichomes", "Fan leaves yellowed/fallen", "Drinking less"],
        "description": "Plain water only. Yellowing fan leaves is normal. Monitor trichomes daily.",
        "checklist": ["Plain pH'd water only", "20% runoff", "Check trichomes daily", "Prepare drying space 60F/60%RH"],
        "common_issues": [],
    },
    "Drying": {
        "duration": "7-14 days", "duration_days": (7, 14),
        "temp_range": (15, 21), "rh_range": (55, 65), "vpd_target": None,
        "light_hours_photo": "Dark", "light_hours_auto": "Dark",
        "ppfd": (0, 0), "next_stage": "Curing",
        "nutrient_needs": "N/A", "watering": "N/A",
        "transition_signs": ["Small stems snap not bend", "Outer buds dry not crunchy", "75% weight loss"],
        "description": "Hang in dark room. Slow dry = quality. 60F/60%RH 'the 60/60 rule'. No fans on buds.",
        "checklist": ["Dark room 60F 60%RH", "Gentle air movement", "Check daily snap test", "7-14 days typical"],
        "common_issues": [
            ("Drying too fast", "Hay smell, harsh. Lower temp, raise RH"),
            ("Drying too slow", "Mold risk. Check daily, slight airflow increase")],
    },
    "Curing": {
        "duration": "2-8+ weeks", "duration_days": (14, 60),
        "temp_range": (15, 21), "rh_range": (58, 65), "vpd_target": None,
        "light_hours_photo": "Dark", "light_hours_auto": "Dark",
        "ppfd": (0, 0), "next_stage": "Harvested",
        "nutrient_needs": "N/A", "watering": "N/A",
        "transition_signs": ["Smooth aroma no hay smell", "Smooth smoke", "4+ weeks passed", "Jar RH stable 58-62%"],
        "description": "Jars 3/4 full. Burp daily 2 weeks then weekly. Target 58-62% RH. Breaks down chlorophyll.",
        "checklist": ["Mason jars 3/4 full", "Hygrometer in jars", "Burp 1-2x daily 2wk", "58-62% RH target",
                      "If >68% leave open 1hr", "After 2wk burp weekly", "Min 4wk cure, 8+ ideal"],
        "common_issues": [
            ("Ammonia smell", "Too wet. Leave open several hours. Check mold."),
            ("Mold in jars", "Remove affected buds immediately. Open jars."),
            ("Too dry/crumbly", "Boveda 62% pack to recover moisture")],
    },
    "Harvested": {
        "duration": "Complete", "duration_days": (0, 0),
        "temp_range": None, "rh_range": None, "vpd_target": None,
        "light_hours_photo": "N/A", "light_hours_auto": "N/A",
        "ppfd": (0, 0), "next_stage": None,
        "nutrient_needs": "N/A", "watering": "N/A",
        "transition_signs": [], "description": "Cycle complete. Record yield, quality, lessons.",
        "checklist": ["Record dry weight", "Rate 1-10", "Note terpenes/aroma", "Document lessons", "Clean grow space"],
        "common_issues": [],
    },
}

# ════════════════════════════════════════════════════════════════════════════
#  SYMPTOM DECISION TREES — scored symptom→diagnosis→fix chains
# ════════════════════════════════════════════════════════════════════════════

SYMPTOM_PATTERNS = [
    {"keywords": ["yellow", "yellowing", "pale"], "leaf_loc": "older",
     "patterns": ["uniform"], "diagnosis": "Nitrogen (N) Deficiency", "confidence": 0.85,
     "rule_id": "nitrogen_def", "note": "Normal in late flower/flush",
     "fix": "Increase N in feed. Check pH 6.0-6.8 soil. Blood meal or worm castings organic."},
    {"keywords": ["yellow", "yellowing"], "leaf_loc": "older",
     "patterns": ["interveinal", "veins green", "between veins", "green veins"],
     "diagnosis": "Magnesium (Mg) Deficiency", "confidence": 0.83, "rule_id": "magnesium_def",
     "note": "Very common with LEDs and coco",
     "fix": "Epsom salt foliar 1tsp/L lights off. Cal-Mag 2-5ml/L. pH 6.0-6.5."},
    {"keywords": ["yellow", "yellowing", "pale"], "leaf_loc": "newer",
     "patterns": ["green veins", "interveinal", "veins stay green"],
     "diagnosis": "Iron (Fe) Deficiency", "confidence": 0.80, "rule_id": "iron_def",
     "note": "Almost always pH too high",
     "fix": "Lower pH: soil <6.5, hydro <6.0. Iron chelate foliar if pH correct."},
    {"keywords": ["yellow", "pale"], "leaf_loc": "newer",
     "patterns": ["uniform", "all over", "entire leaf"],
     "diagnosis": "Sulfur (S) Deficiency", "confidence": 0.65, "rule_id": "sulfur_def",
     "note": "Rare — usually RO water", "fix": "Epsom salt. Check if using RO water."},
    {"keywords": ["brown", "spots", "spotting"], "leaf_loc": "newer",
     "patterns": ["spots", "speckled", "crispy"],
     "diagnosis": "Calcium (Ca) Deficiency", "confidence": 0.80, "rule_id": "calcium_def",
     "fix": "Cal-Mag 2-5ml/L. pH above 6.0 soil. Essential for LED/coco/RO water."},
    {"keywords": ["burnt", "crispy", "brown"], "leaf_loc": "older",
     "patterns": ["edges", "margins", "border"],
     "diagnosis": "Potassium (K) Deficiency", "confidence": 0.83, "rule_id": "potassium_def",
     "note": "Edges/margins = K def. Tips only = nute burn.",
     "fix": "Increase K in bloom feed. Check pH 6.0-7.0 soil."},
    {"keywords": ["burnt", "brown"], "leaf_loc": "any",
     "patterns": ["tips only", "just the tips", "tip burn"],
     "diagnosis": "Nutrient Burn (Overfeeding)", "confidence": 0.88, "rule_id": "nute_burn",
     "fix": "Reduce nutrient strength 20-30%. Flush if severe."},
    {"keywords": ["dark green", "very dark", "black green"],
     "leaf_loc": "any", "patterns": ["claw", "clawing", "curling down", "talons"],
     "diagnosis": "Nitrogen (N) Toxicity", "confidence": 0.86, "rule_id": "nitrogen_def",
     "fix": "Flush 3x pot volume. Reduce N. Switch to bloom nutes if in flower."},
    {"keywords": ["purple", "red"], "leaf_loc": "any",
     "patterns": ["stems", "petioles", "stalks"],
     "diagnosis": "Phosphorus (P) Deficiency or Genetics", "confidence": 0.60, "rule_id": "phosphorus_def",
     "note": "Purple stems alone may be genetic. If paired with slow growth, treat P def.",
     "fix": "Check root zone temp >15C. Increase P. Bone meal organic. pH >6.0 soil."},
    {"keywords": ["curling", "curl", "taco"], "leaf_loc": "any",
     "patterns": ["up", "upward", "taco", "canoe"],
     "diagnosis": "Heat Stress or Light Stress", "confidence": 0.78, "rule_id": "temp_alert",
     "fix": "Raise light. Lower temperature. Increase airflow. Check PPFD <800."},
    {"keywords": ["drooping", "droop", "wilting", "wilt", "limp"],
     "leaf_loc": "any", "patterns": ["all", "whole plant", "everything"],
     "diagnosis": "Overwatering or Underwatering", "confidence": 0.75, "rule_id": "overwater",
     "note": "Lift pot: heavy=overwater, light=underwater",
     "fix": "Overwater: let dry, improve drainage. Underwater: water slowly to runoff."},
    {"keywords": ["twisted", "distorted", "wrinkled", "deformed"],
     "leaf_loc": "newer", "patterns": ["new growth", "top", "growing tip"],
     "diagnosis": "Zinc (Zn) or Calcium (Ca) Deficiency", "confidence": 0.72, "rule_id": "zinc_def",
     "fix": "Check pH 5.8-6.5. Reduce P (high P locks out Zn). Cal-Mag."},
    {"keywords": ["stretching", "lanky", "tall", "thin", "spindly"],
     "leaf_loc": "any", "patterns": ["internodes", "spacing", "tall"],
     "diagnosis": "Insufficient Light", "confidence": 0.82, "rule_id": "temp_alert",
     "fix": "Lower light closer. Increase intensity. Check PPFD is 400-600 for veg, 600-900 flower."},
    {"keywords": ["slow", "stunted", "stopped", "not growing"],
     "leaf_loc": "any", "patterns": ["growth", "growing"],
     "diagnosis": "Root Bound, pH Lockout, or Environmental Stress", "confidence": 0.60,
     "rule_id": "ph_lockout", "fix": "Check roots (transplant if bound). Check pH. Check temp/VPD."},
    {"keywords": ["web", "webbing", "dots", "stippling", "speckled"],
     "leaf_loc": "any", "patterns": ["underside", "under leaves", "tiny"],
     "diagnosis": "Spider Mites", "confidence": 0.85, "rule_id": "spider_mites",
     "fix": "Neem oil lights off. Insecticidal soap. Predatory mites. Repeat every 3d for 2wk."},
    {"keywords": ["flies", "fly", "gnat", "gnats"], "leaf_loc": "any",
     "patterns": ["soil", "surface", "small", "black"],
     "diagnosis": "Fungus Gnats", "confidence": 0.88, "rule_id": "fungus_gnats",
     "fix": "Let soil dry. Yellow sticky traps. BTi/mosquito bits in water. DE on surface."},
    {"keywords": ["silver", "bronze", "streaks", "scarring"],
     "leaf_loc": "any", "patterns": ["leaves", "surface"],
     "diagnosis": "Thrips", "confidence": 0.80, "rule_id": "thrips",
     "fix": "Spinosad spray. Neem oil. Blue sticky traps."},
    {"keywords": ["white", "powder", "powdery", "fuzzy"],
     "leaf_loc": "any", "patterns": ["surface", "patches", "circular", "leaves"],
     "diagnosis": "Powdery Mildew", "confidence": 0.87, "rule_id": "powdery_mildew",
     "fix": "Remove affected leaves. K bicarbonate spray. Milk spray 1:9. Lower RH<50%. Improve airflow."},
    {"keywords": ["mold", "fuzzy", "gray", "grey", "rot"],
     "leaf_loc": "any", "patterns": ["bud", "cola", "inside", "mushy"],
     "diagnosis": "Bud Rot (Botrytis)", "confidence": 0.90, "rule_id": "bud_rot",
     "fix": "EMERGENCY: Remove all affected buds. Cut 2in below. RH<45%. Harvest early if widespread. Do NOT consume."},
    {"keywords": ["slimy", "mushy", "brown", "smell"],
     "leaf_loc": "any", "patterns": ["roots", "root", "base", "stem"],
     "diagnosis": "Root Rot (Pythium)", "confidence": 0.85, "rule_id": "root_rot",
     "fix": "Improve drainage/aeration. H2O2 root drench. Hydroguard/beneficial bacteria. Check water temp <22C."},
    {"keywords": ["bleached", "white", "pale", "albino"],
     "leaf_loc": "newer", "patterns": ["top", "closest to light", "upper"],
     "diagnosis": "Light Burn", "confidence": 0.84, "rule_id": "temp_alert",
     "fix": "Raise light 4-6 inches. Dim if dimmable. Check PPFD — stay below 900 in flower."},
    {"keywords": ["foxtail", "foxtailing", "spire", "tower"],
     "leaf_loc": "any", "patterns": ["bud", "cola", "top"],
     "diagnosis": "Heat/Light Stress (Foxtailing)", "confidence": 0.82, "rule_id": "temp_alert",
     "fix": "Lower canopy temp <28C. Raise light. Improve airflow. Not always bad — some strains foxtail genetically."},
    {"keywords": ["curling", "curl", "hook"],
     "leaf_loc": "any", "patterns": ["down", "downward", "claw", "droop"],
     "diagnosis": "Nitrogen Toxicity or Overwatering", "confidence": 0.77, "rule_id": "nitrogen_def",
     "note": "Dark green + claw = N tox. Light green + droop = overwater.",
     "fix": "If dark green: flush and reduce N. If light/limp: let dry out, improve drainage."},
    {"keywords": ["aphid", "aphids", "sticky", "honeydew"],
     "leaf_loc": "any", "patterns": ["underside", "colony", "cluster", "ants"],
     "diagnosis": "Aphids", "confidence": 0.85, "rule_id": "aphids",
     "fix": "Spray off with water. Neem oil. Insecticidal soap. Ladybugs. Check for ants (they farm aphids)."},
    {"keywords": ["manganese", "brown", "spots", "necrosis"],
     "leaf_loc": "newer", "patterns": ["between veins", "interveinal", "tan"],
     "diagnosis": "Manganese (Mn) Deficiency", "confidence": 0.72, "rule_id": "manganese_def",
     "note": "Usually caused by high pH lockout",
     "fix": "Lower pH to 6.0-6.5 soil / 5.5-6.0 hydro. Foliar manganese sulfate."},
    {"keywords": ["boron", "hollow", "brittle", "cracked"],
     "leaf_loc": "newer", "patterns": ["stem", "thick", "rough", "growing tip"],
     "diagnosis": "Boron (B) Deficiency", "confidence": 0.65, "rule_id": "boron_def",
     "note": "Rare. Usually from RO water without remineralization.",
     "fix": "Borax at 1/4 tsp per gallon. Check pH. Avoid excess calcium (blocks boron uptake)."},
]

# ════════════════════════════════════════════════════════════════════════════
#  NUTRIENT ISSUES DATABASE
# ════════════════════════════════════════════════════════════════════════════

NUTRIENT_ISSUES = {
    "Nitrogen (N)": {"symbol": "N", "mobile": True,
        "deficiency": {"symptoms": ["Uniform yellowing older/lower leaves", "Pale green overall", "Reduced growth", "Smaller leaves", "Early leaf drop bottom up"],
            "affected_leaves": "Older (bottom) first", "fix": ["Increase N in feed", "Check pH 6.0-6.8 soil", "Blood meal/worm castings organic", "Foliar dilute N solution"],
            "notes": "Most common deficiency. Normal in late flower/flush."},
        "toxicity": {"symptoms": ["Very dark green waxy leaves", "Clawing tips down", "Slow flowering", "Weak stems"], "fix": ["Flush 3x pot volume", "Reduce N", "Switch to bloom nutes"]}},
    "Phosphorus (P)": {"symbol": "P", "mobile": True,
        "deficiency": {"symptoms": ["Dark/bluish-green leaves", "Purple/red stems", "Brown patches older leaves", "Slow growth", "Poor bud development"],
            "affected_leaves": "Older first", "fix": ["Increase P bloom boosters", "pH must be above 6.0 soil", "Root temp above 15C", "Bone meal/bat guano organic"],
            "notes": "Cold roots commonly cause P lockout."},
        "toxicity": {"symptoms": ["Zn/Fe lockout", "Interveinal yellowing new growth", "Burnt tips"], "fix": ["Flush", "Reduce PK boosters"]}},
    "Potassium (K)": {"symbol": "K", "mobile": True,
        "deficiency": {"symptoms": ["Brown crispy burnt leaf MARGINS/EDGES", "Yellowing between veins older", "Weak stems", "Airy buds"],
            "affected_leaves": "Older — edges/margins", "fix": ["Increase K in bloom feed", "pH 6.0-7.0 soil", "Kelp meal organic", "Flush first if salt buildup"],
            "notes": "Common in flower. K def = edges. Nute burn = tips only."},
        "toxicity": {"symptoms": ["Ca/Mg lockout", "Salt buildup"], "fix": ["Flush", "Reduce K"]}},
    "Calcium (Ca)": {"symbol": "Ca", "mobile": False,
        "deficiency": {"symptoms": ["Distorted curled new growth", "Brown spots on new leaves", "Crispy new leaves", "Hollow weak stems"],
            "affected_leaves": "New (upper) growth first", "fix": ["Cal-Mag 2-5ml/L", "pH above 6.0 soil", "Dolomite lime soil", "Essential for LED/coco/RO"],
            "notes": "Very common with LEDs, coco, RO water."},
        "toxicity": {"symptoms": ["K/Mg/Fe lockout", "Wilting"], "fix": ["Flush", "Reduce Cal-Mag"]}},
    "Magnesium (Mg)": {"symbol": "Mg", "mobile": True,
        "deficiency": {"symptoms": ["Interveinal yellowing older (veins GREEN, tissue yellow)", "Leaves curl upward", "Red/purple margins", "Brown crispy spots advanced"],
            "affected_leaves": "Older/middle first", "fix": ["Epsom salt foliar 1tsp/L lights off", "Cal-Mag 2-5ml/L", "pH 6.0-6.5", "Dolomite lime long-term"],
            "notes": "Second most common def. LEDs and coco prone. Interveinal = Mg, uniform = N."},
        "toxicity": {"symptoms": ["Ca lockout", "Dark droopy leaves"], "fix": ["Flush", "Reduce Mg"]}},
    "Iron (Fe)": {"symbol": "Fe", "mobile": False,
        "deficiency": {"symptoms": ["New leaves yellow with green veins", "Pale/yellow new growth", "Complete bleaching severe"],
            "affected_leaves": "Newest growth first", "fix": ["Lower pH: soil <6.5, hydro <6.0", "Iron chelate foliar", "Reduce Mn (competes)"],
            "notes": "Almost always pH too high, not actual iron shortage."},
        "toxicity": {"symptoms": ["Bronze/brown spots", "Leaf necrosis"], "fix": ["Raise pH slightly", "Flush"]}},
    "Zinc (Zn)": {"symbol": "Zn", "mobile": False,
        "deficiency": {"symptoms": ["Small thin new leaves", "Twisted wrinkled growth", "Short internodes", "Leaf tips die back"],
            "affected_leaves": "New growth", "fix": ["pH 5.8-6.5", "Zinc sulfate foliar", "Reduce P (high P locks out Zn)", "Kelp extract"],
            "notes": "Often caused by high pH or excessive P."},
        "toxicity": {"symptoms": ["Fe deficiency symptoms"], "fix": ["Flush", "Reduce zinc"]}},
    "Manganese (Mn)": {"symbol": "Mn", "mobile": False,
        "deficiency": {"symptoms": ["Interveinal chlorosis young leaves + tan dead spots", "Mottled appearance"],
            "affected_leaves": "Young leaves", "fix": ["Lower pH below 6.5", "Mn sulfate foliar", "Check Fe competition"],
            "notes": "Rare alone. pH-related. Similar to Fe but has dead spots within yellowed areas."},
        "toxicity": {"symptoms": ["Brown/orange spots", "Fe lockout"], "fix": ["Raise pH 6.0+", "Flush"]}},
    "Sulfur (S)": {"symbol": "S", "mobile": False,
        "deficiency": {"symptoms": ["Uniform yellowing NEW leaves (unlike N)", "Slow stunted growth", "Stiff brittle leaves"],
            "affected_leaves": "New leaves first (unlike N=old)", "fix": ["Epsom salt (has S)", "Gypsum", "Check if using RO water"],
            "notes": "Very rare. Usually only RO water. S=top, N=bottom."},
        "toxicity": {"symptoms": ["Small leaves", "Slow growth"], "fix": ["Flush"]}},
    "Boron (B)": {"symbol": "B", "mobile": False,
        "deficiency": {"symptoms": ["Thick stunted new growth", "Hollow rough stems", "Growing tips die", "Thick brittle leaves"],
            "affected_leaves": "New growth, tips", "fix": ["Boric acid VERY dilute 1/4tsp/gal", "pH 6.0-6.5", "Careful — toxicity easy"],
            "notes": "Rare. Thin line between deficiency and toxicity."},
        "toxicity": {"symptoms": ["Leaf tip/margin burn", "Yellowing", "Leaf drop"], "fix": ["Flush heavily — serious"]}},
}

PH_LOCKOUT = {
    "soil": {"optimal": (6.0, 6.8), "sweet_spot": (6.3, 6.5),
        "lockout_zones": {"below_5.5": ["Calcium","Magnesium","Phosphorus"], "below_5.0": ["Nitrogen","Potassium","Sulfur"],
            "above_7.0": ["Iron","Manganese","Zinc","Copper","Boron"], "above_7.5": ["Phosphorus","Most micronutrients"]}},
    "hydro_coco": {"optimal": (5.5, 6.5), "sweet_spot": (5.8, 6.0),
        "lockout_zones": {"below_5.0": ["Calcium","Magnesium","Phosphorus"], "below_4.5": ["Most nutrients"],
            "above_6.5": ["Iron","Manganese","Zinc"], "above_7.0": ["Phosphorus","Most micronutrients"]}},
}

# ════════════════════════════════════════════════════════════════════════════
#  PESTS DATABASE
# ════════════════════════════════════════════════════════════════════════════

PESTS = {
    "Spider Mites": {"signs": ["Tiny dots stippling on leaf tops", "Fine webbing undersides", "Speckled/bronzed leaves"],
        "severity": "High", "treatment": ["Neem oil lights off", "Insecticidal soap", "Spinosad", "Predatory mites",
        "Lower temp raise humidity", "Repeat every 3 days for 2 weeks"],
        "prevention": "Inspect new plants, clean room, airflow", "urgency": "Immediate"},
    "Fungus Gnats": {"signs": ["Tiny black flies near soil", "Larvae in top soil", "Seedling damage"],
        "severity": "Low-Medium", "treatment": ["Let soil dry", "Yellow sticky traps", "BTi/mosquito bits", "DE on surface", "Sand/perlite top layer"],
        "prevention": "Don't overwater, drainage, sterile soil", "urgency": "Low"},
    "Thrips": {"signs": ["Silver/bronze streaks", "Tiny thin insects", "Black frass on leaves"],
        "severity": "Medium-High", "treatment": ["Spinosad spray", "Neem oil", "Blue sticky traps", "Predatory mites Amblyseius"],
        "prevention": "Screen intakes, inspect regularly, quarantine", "urgency": "Moderate"},
    "Aphids": {"signs": ["Clusters of small insects stems/undersides", "Sticky honeydew", "Curled distorted growth"],
        "severity": "Medium", "treatment": ["Strong water spray", "Neem oil/insecticidal soap", "Ladybugs", "Pyrethrin last resort"],
        "prevention": "Companion planting, inspection, beneficials", "urgency": "Moderate"},
    "Whiteflies": {"signs": ["Tiny white moths undersides", "Fly up when disturbed", "Sticky yellowing sooty mold"],
        "severity": "Medium", "treatment": ["Yellow sticky traps", "Neem oil", "Insecticidal soap", "Encarsia wasp"],
        "prevention": "Screen vents, quarantine", "urgency": "Moderate"},
    "Powdery Mildew": {"signs": ["White powdery patches", "Circular spots spreading", "Curling yellowing under mildew"],
        "severity": "High", "treatment": ["Remove leaves immediately", "K bicarbonate spray", "Milk spray 1:9", "Airflow", "RH<50%"],
        "prevention": "Airflow, defoliation, RH<60%, don't crowd", "urgency": "Immediate"},
    "Bud Rot (Botrytis)": {"signs": ["Gray fuzzy mold INSIDE buds", "Yellowing sugar leaves in cola", "Mushy brown bud interior"],
        "severity": "Critical", "treatment": ["REMOVE affected buds cut 2in below", "Increase airflow", "RH<45%", "Harvest early if widespread", "Do NOT consume moldy buds"],
        "prevention": "RH<50% flower, airflow, defoliate, don't crowd", "urgency": "Emergency"},
    "Root Rot": {"signs": ["Brown slimy smelly roots", "Wilting despite wet medium", "Slow growth yellowing"],
        "severity": "High", "treatment": ["Hydroguard/beneficials", "H2O2 drench 3% 1ml/L", "Improve drainage", "Let dry more", "Hydro: water temp 18-20C"],
        "prevention": "Don't overwater, drainage, fabric pots, beneficials", "urgency": "Urgent"},
}

# ════════════════════════════════════════════════════════════════════════════
#  TRAINING TECHNIQUES
# ════════════════════════════════════════════════════════════════════════════

TRAINING_TECHNIQUES = {
    "LST (Low Stress Training)": {"difficulty": "Beginner", "stage": "Veg after 4+ nodes", "auto_safe": True, "recovery_days": 0, "yield_boost": "20-40%",
        "description": "Bend and tie branches to expose lower growth. Even canopy, no cutting needed.",
        "steps": ["Wait 4-5 nodes", "Bend main stem 90deg with soft wire", "Anchor to pot edge", "Adjust every 2-3 days", "Stop early flower"],
        "benefits": ["Even canopy", "More colas", "No recovery", "Auto-safe"], "cautions": ["Be gentle stems can snap", "Use soft ties"]},
    "Topping": {"difficulty": "Beginner", "stage": "Veg 5-6 nodes min", "auto_safe": False, "recovery_days": 3, "yield_boost": "30-50%",
        "description": "Cut main tip to split into two. Creates bushier plant with more cola sites.",
        "steps": ["Wait 5-6 nodes", "Clean sharp cut above node 3-5", "Two branches grow from that node", "Wait 5-7 days before more training"],
        "benefits": ["Doubles colas each top", "Shorter bushier", "Great with LST"], "cautions": ["NOT for autos", "Don't top sick plants", "Never in flower"]},
    "FIM (F*ck I Missed)": {"difficulty": "Intermediate", "stage": "Veg after 4+ nodes", "auto_safe": False, "recovery_days": 2, "yield_boost": "30-60%",
        "description": "Cut 80% of growth tip. Can produce 3-8 new tops but less predictable than topping.",
        "steps": ["Find newest tip", "Cut ~80% leaving 20%", "Multiple growth points emerge", "Faster recovery than topping"],
        "benefits": ["3-8 new tops possible", "Less stress than topping"], "cautions": ["Less predictable", "Not for autos", "Practice needed"]},
    "SCROG (Screen of Green)": {"difficulty": "Intermediate", "stage": "Late Veg through Early Flower", "auto_safe": True, "recovery_days": 0, "yield_boost": "40-60%",
        "description": "Horizontal net creates perfectly flat canopy. Maximum light efficiency.",
        "steps": ["Install net 12-18in above pots", "Top/LST first recommended", "Tuck branches under as they grow through", "Fill 60-70% before flip", "Stop tucking wk2 flower", "Lollipop below screen"],
        "benefits": ["Maximum light efficiency", "Even buds", "Height control", "Great yields"], "cautions": ["Can't move plants", "Plan pot placement", "Commitment required"]},
    "Supercropping": {"difficulty": "Intermediate", "stage": "Veg and Early Flower", "auto_safe": False, "recovery_days": 3, "yield_boost": "10-20%",
        "description": "Squeeze stem until inner fibers break, bend 90deg. Heals into strengthened knuckle.",
        "steps": ["Choose tall branch", "Squeeze between fingers roll gently", "Feel inner snap outer skin intact", "Branch droops 90deg", "Tape if needed", "Knuckle forms 3-7 days"],
        "benefits": ["Height control no cutting", "Strengthened stems at knuckle", "Can do early flower"], "cautions": ["Practice on lower branches", "Don't tear skin", "Not for thin stems"]},
    "Defoliation": {"difficulty": "Intermediate-Advanced", "stage": "Late Veg and Day 21 Flower", "auto_safe": False, "recovery_days": 2, "yield_boost": "10-30%",
        "description": "Strategic removal of fan leaves for light/airflow. Schwazze technique: heavy defoliation day 1 and day 21 of flower.",
        "steps": ["Veg: remove leaves blocking bud sites", "Day 1 flower: moderate defoliation", "Day 21: heavy schwazze", "Only fan leaves never sugar leaves"],
        "benefits": ["Better light penetration", "Airflow mold prevention", "Energy to buds"], "cautions": ["NEVER autos", "Don't defoliate sick plants", "Start conservative"]},
    "Lollipopping": {"difficulty": "Beginner-Intermediate", "stage": "Late Veg / first days Flower", "auto_safe": False, "recovery_days": 1, "yield_boost": "5-15%",
        "description": "Remove lower 1/3 growth to focus on top colas. Eliminates popcorn buds.",
        "steps": ["Identify lower 1/3", "Remove small branches and sites", "Remove lower fans", "Gradual over 2-3 days"],
        "benefits": ["No popcorn buds", "Better airflow", "Energy to tops", "Easier maintenance"], "cautions": ["Not too much at once", "Before or first 3-5d flower"]},
    "Mainlining (Manifolding)": {"difficulty": "Advanced", "stage": "Veg extended", "auto_safe": False, "recovery_days": 5, "yield_boost": "30-60%",
        "description": "Symmetrical manifold of 8-16 equal colas through repeated topping and training.",
        "steps": ["Top above node 3 at 5-6 nodes", "Remove all below", "LST two branches horizontal", "Grow 3-4 nodes top again", "Repeat for 8 or 16 tops"],
        "benefits": ["Perfect symmetry", "Equal cola sizes", "Impressive yields"], "cautions": ["Adds 3-5 weeks veg", "NOT for autos", "Patience required"]},
}

# ════════════════════════════════════════════════════════════════════════════
#  CLONING & BREEDING KNOWLEDGE
# ════════════════════════════════════════════════════════════════════════════

CLONING_GUIDE = {
    "mother_selection": {"title": "Selecting a Mother Plant", "tips": [
        "Choose healthiest most vigorous plant", "Mid-veg 4-8 weeks old ideal",
        "Select for vigor, structure, pest resistance, terpenes",
        "Keep under 18/6+ light permanently", "Feed 50-75% strength",
        "Take test clone and flower to verify quality first", "Label everything"]},
    "taking_cuttings": {"title": "Taking Cuttings", "tips": [
        "Sterile razor blade (alcohol between cuts)", "4-6 inch branches 2-3 nodes",
        "Cut at 45deg angle", "Immediately into water/rooting solution",
        "Remove lower leaves keep 2-3 sets top", "Trim big fans 50%",
        "Scrape bottom 1 inch stem", "Dip in rooting gel (gel > powder)",
        "Take 20-30% extra — not all will root", "Lower branches root faster"]},
    "rooting_environment": {"title": "Rooting Environment", "tips": [
        "Humidity dome/propagation tray clear lid", "75-80F (24-27C) heat mat helps",
        "80-100% RH first 3-5 days then reduce", "Low light 100-200 PPFD T5/dim LED",
        "18/6 light schedule", "Mist dome walls not clones directly",
        "Crack vents day 3", "Remove dome when roots show 7-14 days"]},
    "success_tips": {"title": "Maximizing Success Rate", "tips": [
        "Lower branches have more rooting hormones", "Avoid cloning from flowering plant",
        "pH rooting water 5.8-6.0", "Moist not soaked medium",
        "Wilting days 1-3 is normal", "Don't tug to check roots",
        "Target 90%+ with good technique"]},
    "success_factors": {
        "optimal_temp": (24, 27), "optimal_rh": (80, 95), "optimal_ph": (5.8, 6.0),
        "method_success_rates": {
            "Rooting Gel + Rapid Rooter": 0.88, "Rooting Powder + Rockwool": 0.80,
            "Clonex + Aeroponic Cloner": 0.92, "Water Cloning (no hormone)": 0.60,
            "Aloe Vera Gel (organic)": 0.70, "Honey (organic)": 0.55}},
}

BREEDING_GUIDE = {
    "basics": {"title": "Breeding Basics", "content": [
        "Males produce pollen sacs, females produce pistils/buds.",
        "Controlled pollination: isolate male branch, collect pollen, apply to one female branch.",
        "Seeds mature 4-6 weeks after pollination.", "F1 = first cross. F2 = F1 selfed. BX = backcross.",
        "Feminized seeds: reverse female with STS or colloidal silver.", "Label EVERYTHING."]},
    "pollen_collection": {"title": "Collecting Pollen", "content": [
        "Isolate male when pre-flowers show", "Parchment paper under sacs",
        "Sacs open naturally collect dust", "Store airtight with desiccant",
        "Viable weeks room temp, months frozen", "Apply with small brush to pistils"]},
    "phenotype_hunting": {"title": "Phenotype Hunting", "content": [
        "Grow 10-20+ seeds from cross", "Score each on vigor/yield/terps/resin/resistance",
        "1-10 scale each category", "Clone ALL promising phenos BEFORE flowering",
        "Flower originals, keep clones in veg", "Select keepers — best 1-3 phenos",
        "Promote keepers to mother status"]},
    "generation_guide": {
        "F1": "First cross — max hybrid vigor, wide variation",
        "F2": "F1 x F1 — wider variation, recessives emerge",
        "F3": "F2 x F2 — starting to stabilize",
        "F4+": "More stable and predictable",
        "BX1": "Backcross: F1 x Parent — reinforces parent traits",
        "S1": "Selfed — female x own reversed pollen (feminized seeds)"},
    "sex_identification": {
        "male_signs": ["Round ball clusters at nodes", "Sacs on small stems", "Show sex 1-2wk before females", "Taller leggier usually"],
        "female_signs": ["White pistils from calyx at nodes", "Pistils in pairs", "Pre-flowers at main stem nodes", "Shorter bushier usually"],
        "hermie_signs": ["Both sacs and pistils", "Nanners — banana shapes in buds", "Usually stress-caused", "Remove nanners or harvest early"]},
}

# ════════════════════════════════════════════════════════════════════════════
#  STRAIN LIBRARY
# ════════════════════════════════════════════════════════════════════════════

STRAIN_LIBRARY = [
    # ─── Indica ────────────────────────────────────────────────────────────
    {"name": "Northern Lights", "breeder": "Sensi Seeds", "strain_type": "Indica", "genetics": "Afghani x Thai",
     "flowering_weeks_min": 7, "flowering_weeks_max": 9, "thc_range": "16-21%", "difficulty": "Easy",
     "description": "Legendary indica. Resinous, fast, forgiving.", "terpenes": "Myrcene, Caryophyllene, Limonene",
     "yield_indoor": "450-550 g/m²", "is_autoflower": 0},
    {"name": "Granddaddy Purple", "breeder": "Ken Estes", "strain_type": "Indica", "genetics": "Purple Urkle x Big Bud",
     "flowering_weeks_min": 8, "flowering_weeks_max": 11, "thc_range": "17-23%", "difficulty": "Moderate",
     "description": "Deep purple buds. Grape/berry aroma. Heavy relaxation.", "terpenes": "Myrcene, Pinene, Caryophyllene",
     "yield_indoor": "400-500 g/m²", "is_autoflower": 0},
    {"name": "Bubba Kush", "breeder": "Unknown", "strain_type": "Indica", "genetics": "OG Kush x Unknown Indica",
     "flowering_weeks_min": 8, "flowering_weeks_max": 9, "thc_range": "15-22%", "difficulty": "Easy",
     "description": "Stocky dense plant. Coffee/chocolate flavors. Classic nighttime.", "terpenes": "Caryophyllene, Limonene, Myrcene",
     "yield_indoor": "350-450 g/m²", "is_autoflower": 0},
    {"name": "Purple Punch", "breeder": "Symbiotic Genetics", "strain_type": "Indica", "genetics": "Larry OG x Granddaddy Purple",
     "flowering_weeks_min": 7, "flowering_weeks_max": 9, "thc_range": "18-25%", "difficulty": "Easy",
     "description": "Grape candy flavor. Beautiful purple hues. Very sedating.", "terpenes": "Limonene, Caryophyllene, Myrcene",
     "yield_indoor": "450-500 g/m²", "is_autoflower": 0},
    {"name": "Hindu Kush", "breeder": "Landrace", "strain_type": "Indica", "genetics": "Landrace (Hindu Kush Mountains)",
     "flowering_weeks_min": 7, "flowering_weeks_max": 8, "thc_range": "15-20%", "difficulty": "Easy",
     "description": "Pure landrace indica. Earthy/sandalwood. Extremely resilient.", "terpenes": "Myrcene, Caryophyllene, Pinene",
     "yield_indoor": "350-450 g/m²", "is_autoflower": 0},
    {"name": "Do-Si-Dos", "breeder": "Archive Seed Bank", "strain_type": "Indica", "genetics": "OG Kush Breath x Face Off OG",
     "flowering_weeks_min": 8, "flowering_weeks_max": 9, "thc_range": "19-30%", "difficulty": "Moderate",
     "description": "Pungent lime/earthy. Dense colorful buds. Potent body high.", "terpenes": "Limonene, Linalool, Caryophyllene",
     "yield_indoor": "400-500 g/m²", "is_autoflower": 0},
    {"name": "Afghan Kush", "breeder": "Landrace", "strain_type": "Indica", "genetics": "Landrace (Afghanistan)",
     "flowering_weeks_min": 7, "flowering_weeks_max": 8, "thc_range": "15-20%", "difficulty": "Easy",
     "description": "100% pure indica. Earthy hash flavor. Deeply relaxing.", "terpenes": "Myrcene, Pinene, Caryophyllene",
     "yield_indoor": "350-450 g/m²", "is_autoflower": 0},
    {"name": "Blueberry", "breeder": "DJ Short", "strain_type": "Indica", "genetics": "Afghani x Thai x Purple Thai",
     "flowering_weeks_min": 8, "flowering_weeks_max": 10, "thc_range": "17-24%", "difficulty": "Moderate",
     "description": "Award-winning. Genuine blueberry flavor. Beautiful colors.", "terpenes": "Myrcene, Pinene, Caryophyllene",
     "yield_indoor": "400-500 g/m²", "is_autoflower": 0},

    # ─── Sativa ────────────────────────────────────────────────────────────
    {"name": "Sour Diesel", "breeder": "Unknown/AJ", "strain_type": "Sativa", "genetics": "Chemdawg 91 x Super Skunk",
     "flowering_weeks_min": 10, "flowering_weeks_max": 12, "thc_range": "20-25%", "difficulty": "Moderate",
     "description": "Legendary sativa. Pungent diesel. Energizing cerebral high.", "terpenes": "Caryophyllene, Myrcene, Limonene",
     "yield_indoor": "450-550 g/m²", "is_autoflower": 0},
    {"name": "Amnesia Haze", "breeder": "Soma Seeds", "strain_type": "Sativa", "genetics": "South Asian x Jamaican x Afghani/Hawaiian",
     "flowering_weeks_min": 10, "flowering_weeks_max": 12, "thc_range": "20-25%", "difficulty": "Hard",
     "description": "Amsterdam legend. Lemony haze. Long flower but worth it.", "terpenes": "Terpinolene, Myrcene, Limonene",
     "yield_indoor": "500-600 g/m²", "is_autoflower": 0},
    {"name": "Jack Herer", "breeder": "Sensi Seeds", "strain_type": "Sativa", "genetics": "Haze x Northern Lights #5 x Shiva Skunk",
     "flowering_weeks_min": 8, "flowering_weeks_max": 10, "thc_range": "18-24%", "difficulty": "Moderate",
     "description": "Named after cannabis activist. Pine/spice. Creative & focused.", "terpenes": "Terpinolene, Pinene, Caryophyllene",
     "yield_indoor": "400-500 g/m²", "is_autoflower": 0},
    {"name": "Green Crack", "breeder": "Cecil C", "strain_type": "Sativa", "genetics": "Skunk #1 x Unknown Sativa",
     "flowering_weeks_min": 7, "flowering_weeks_max": 9, "thc_range": "15-25%", "difficulty": "Easy",
     "description": "Tangy mango. Sharp energy. Great daytime strain.", "terpenes": "Myrcene, Caryophyllene, Pinene",
     "yield_indoor": "450-550 g/m²", "is_autoflower": 0},
    {"name": "Super Lemon Haze", "breeder": "Green House Seeds", "strain_type": "Sativa", "genetics": "Lemon Skunk x Super Silver Haze",
     "flowering_weeks_min": 9, "flowering_weeks_max": 10, "thc_range": "19-25%", "difficulty": "Moderate",
     "description": "Zesty lemon. Uplifting and social. Two-time Cannabis Cup winner.", "terpenes": "Terpinolene, Caryophyllene, Myrcene",
     "yield_indoor": "500-600 g/m²", "is_autoflower": 0},
    {"name": "Durban Poison", "breeder": "Landrace", "strain_type": "Sativa", "genetics": "Landrace (South Africa)",
     "flowering_weeks_min": 8, "flowering_weeks_max": 9, "thc_range": "15-25%", "difficulty": "Easy",
     "description": "Pure sativa landrace. Sweet anise/licorice. Uplifting.", "terpenes": "Terpinolene, Myrcene, Ocimene",
     "yield_indoor": "350-450 g/m²", "is_autoflower": 0},
    {"name": "Strawberry Cough", "breeder": "Kyle Kushman", "strain_type": "Sativa", "genetics": "Strawberry Fields x Haze",
     "flowering_weeks_min": 9, "flowering_weeks_max": 10, "thc_range": "18-23%", "difficulty": "Moderate",
     "description": "Sweet strawberry smell. Uplifting euphoria. Smooth smoke.", "terpenes": "Pinene, Myrcene, Caryophyllene",
     "yield_indoor": "400-500 g/m²", "is_autoflower": 0},
    {"name": "Maui Wowie", "breeder": "Landrace", "strain_type": "Sativa", "genetics": "Landrace (Hawaii)",
     "flowering_weeks_min": 9, "flowering_weeks_max": 11, "thc_range": "13-20%", "difficulty": "Moderate",
     "description": "Tropical pineapple/citrus. Light energizing effects.", "terpenes": "Myrcene, Pinene, Terpinolene",
     "yield_indoor": "350-450 g/m²", "is_autoflower": 0},

    # ─── Hybrid ────────────────────────────────────────────────────────────
    {"name": "Blue Dream", "breeder": "DJ Short", "strain_type": "Hybrid", "genetics": "Blueberry x Haze",
     "flowering_weeks_min": 9, "flowering_weeks_max": 10, "thc_range": "17-24%", "difficulty": "Easy",
     "description": "California classic. Sweet berry. Balanced effects. Beginner-friendly.", "terpenes": "Myrcene, Caryophyllene, Pinene",
     "yield_indoor": "500-600 g/m²", "is_autoflower": 0},
    {"name": "OG Kush", "breeder": "Josh D", "strain_type": "Hybrid", "genetics": "Chemdawg x Lemon Thai x Hindu Kush",
     "flowering_weeks_min": 8, "flowering_weeks_max": 9, "thc_range": "20-25%", "difficulty": "Moderate",
     "description": "West Coast backbone. Fuel/pine/citrus. Iconic.", "terpenes": "Myrcene, Limonene, Caryophyllene",
     "yield_indoor": "400-450 g/m²", "is_autoflower": 0},
    {"name": "Girl Scout Cookies", "breeder": "Cookie Fam", "strain_type": "Hybrid", "genetics": "Durban Poison x OG Kush",
     "flowering_weeks_min": 9, "flowering_weeks_max": 10, "thc_range": "25-28%", "difficulty": "Moderate",
     "description": "Award-winner. Sweet earthy minty. Dense frosty nugs.", "terpenes": "Caryophyllene, Limonene, Humulene",
     "yield_indoor": "350-400 g/m²", "is_autoflower": 0},
    {"name": "White Widow", "breeder": "Green House Seeds", "strain_type": "Hybrid", "genetics": "Brazilian Sativa x South Indian Indica",
     "flowering_weeks_min": 8, "flowering_weeks_max": 9, "thc_range": "18-25%", "difficulty": "Easy",
     "description": "Amsterdam legend. Extremely resinous. Balanced high.", "terpenes": "Myrcene, Caryophyllene, Limonene",
     "yield_indoor": "450-500 g/m²", "is_autoflower": 0},
    {"name": "Gorilla Glue #4", "breeder": "GG Strains", "strain_type": "Hybrid", "genetics": "Chem Sister x Sour Dubb x Chocolate Diesel",
     "flowering_weeks_min": 8, "flowering_weeks_max": 9, "thc_range": "25-30%", "difficulty": "Moderate",
     "description": "Incredibly sticky resin. Diesel/chocolate. Powerhouse.", "terpenes": "Caryophyllene, Myrcene, Limonene",
     "yield_indoor": "500-600 g/m²", "is_autoflower": 0},
    {"name": "Gelato #33", "breeder": "Sherbinskis", "strain_type": "Hybrid", "genetics": "Sunset Sherbet x Thin Mint GSC",
     "flowering_weeks_min": 8, "flowering_weeks_max": 9, "thc_range": "20-25%", "difficulty": "Hard",
     "description": "Dessert flavor. Purple/orange buds. Smooth & potent.", "terpenes": "Limonene, Caryophyllene, Humulene",
     "yield_indoor": "400-500 g/m²", "is_autoflower": 0},
    {"name": "Wedding Cake", "breeder": "Seed Junky", "strain_type": "Hybrid", "genetics": "Triangle Kush x Animal Mints",
     "flowering_weeks_min": 7, "flowering_weeks_max": 9, "thc_range": "24-27%", "difficulty": "Moderate",
     "description": "Rich tangy sweet. Dense resinous. Relaxing but not couch-lock.", "terpenes": "Limonene, Caryophyllene, Myrcene",
     "yield_indoor": "450-550 g/m²", "is_autoflower": 0},
    {"name": "Zkittlez", "breeder": "Terp Hogz", "strain_type": "Indica-dominant", "genetics": "Grape Ape x Grapefruit",
     "flowering_weeks_min": 8, "flowering_weeks_max": 9, "thc_range": "20-23%", "difficulty": "Moderate",
     "description": "Fruit candy terpenes. Beautiful purple/red colors.", "terpenes": "Linalool, Caryophyllene, Humulene",
     "yield_indoor": "400-500 g/m²", "is_autoflower": 0},
    {"name": "Runtz", "breeder": "Cookies", "strain_type": "Hybrid", "genetics": "Zkittlez x Gelato",
     "flowering_weeks_min": 8, "flowering_weeks_max": 9, "thc_range": "19-29%", "difficulty": "Moderate",
     "description": "Sweet fruity candy. Dense colorful nugs. Balanced effects.", "terpenes": "Limonene, Caryophyllene, Linalool",
     "yield_indoor": "400-500 g/m²", "is_autoflower": 0},
    {"name": "GMO Cookies", "breeder": "Mamiko Seeds", "strain_type": "Indica-dominant", "genetics": "GSC x Chemdawg",
     "flowering_weeks_min": 9, "flowering_weeks_max": 10, "thc_range": "24-30%", "difficulty": "Moderate",
     "description": "Garlic/mushroom/onion funk. Extremely potent. Not for beginners.", "terpenes": "Caryophyllene, Myrcene, Limonene",
     "yield_indoor": "450-550 g/m²", "is_autoflower": 0},
    {"name": "Pineapple Express", "breeder": "G13 Labs", "strain_type": "Hybrid", "genetics": "Trainwreck x Hawaiian",
     "flowering_weeks_min": 7, "flowering_weeks_max": 9, "thc_range": "17-25%", "difficulty": "Easy",
     "description": "Tropical pineapple/mango. Energetic & creative. Fun grow.", "terpenes": "Caryophyllene, Limonene, Pinene",
     "yield_indoor": "450-550 g/m²", "is_autoflower": 0},
    {"name": "Chemdawg", "breeder": "Unknown", "strain_type": "Hybrid", "genetics": "Unknown (Thai x Nepalese suspected)",
     "flowering_weeks_min": 9, "flowering_weeks_max": 10, "thc_range": "15-20%", "difficulty": "Moderate",
     "description": "Parent of OG Kush and Sour Diesel. Sharp chemical/diesel.", "terpenes": "Caryophyllene, Myrcene, Humulene",
     "yield_indoor": "400-500 g/m²", "is_autoflower": 0},
    {"name": "Mimosa", "breeder": "Symbiotic Genetics", "strain_type": "Sativa-dominant", "genetics": "Clementine x Purple Punch",
     "flowering_weeks_min": 8, "flowering_weeks_max": 10, "thc_range": "19-27%", "difficulty": "Moderate",
     "description": "Citrus mimosa flavor. Uplifting morning strain. Gorgeous plant.", "terpenes": "Limonene, Myrcene, Linalool",
     "yield_indoor": "450-550 g/m²", "is_autoflower": 0},
    {"name": "Ice Cream Cake", "breeder": "Seed Junky", "strain_type": "Indica-dominant", "genetics": "Wedding Cake x Gelato #33",
     "flowering_weeks_min": 8, "flowering_weeks_max": 9, "thc_range": "20-25%", "difficulty": "Moderate",
     "description": "Creamy vanilla/sugary. Relaxing body effects. Dense frosty nugs.", "terpenes": "Limonene, Caryophyllene, Linalool",
     "yield_indoor": "400-500 g/m²", "is_autoflower": 0},
    {"name": "Trainwreck", "breeder": "Arcata", "strain_type": "Sativa-dominant", "genetics": "Mexican Sativa x Thai x Afghani",
     "flowering_weeks_min": 8, "flowering_weeks_max": 10, "thc_range": "18-25%", "difficulty": "Easy",
     "description": "Fast-hitting sativa hybrid. Pine/lemon/spice. Energizing.", "terpenes": "Terpinolene, Myrcene, Pinene",
     "yield_indoor": "450-500 g/m²", "is_autoflower": 0},
    {"name": "AK-47", "breeder": "Serious Seeds", "strain_type": "Hybrid", "genetics": "Colombian x Mexican x Thai x Afghani",
     "flowering_weeks_min": 7, "flowering_weeks_max": 9, "thc_range": "13-20%", "difficulty": "Easy",
     "description": "Mellow steady buzz despite the name. Earthy/floral. Easy grow.", "terpenes": "Myrcene, Pinene, Caryophyllene",
     "yield_indoor": "400-500 g/m²", "is_autoflower": 0},
    {"name": "Banana Kush", "breeder": "Unknown", "strain_type": "Indica-dominant", "genetics": "Ghost OG x Skunk Haze",
     "flowering_weeks_min": 8, "flowering_weeks_max": 9, "thc_range": "18-25%", "difficulty": "Moderate",
     "description": "Tropical banana flavor. Mellow relaxation. Smooth smoke.", "terpenes": "Limonene, Myrcene, Caryophyllene",
     "yield_indoor": "400-500 g/m²", "is_autoflower": 0},
    {"name": "Skywalker OG", "breeder": "DNA Genetics", "strain_type": "Indica-dominant", "genetics": "Skywalker x OG Kush",
     "flowering_weeks_min": 8, "flowering_weeks_max": 9, "thc_range": "20-30%", "difficulty": "Moderate",
     "description": "Spicy herbal. Heavy indica effects. Great for pain/insomnia.", "terpenes": "Myrcene, Caryophyllene, Limonene",
     "yield_indoor": "400-500 g/m²", "is_autoflower": 0},
    {"name": "Bruce Banner #3", "breeder": "Dark Horse Genetics", "strain_type": "Hybrid", "genetics": "OG Kush x Strawberry Diesel",
     "flowering_weeks_min": 8, "flowering_weeks_max": 10, "thc_range": "24-30%", "difficulty": "Moderate",
     "description": "Named for the Hulk. Massive THC. Diesel/sweet.", "terpenes": "Myrcene, Caryophyllene, Limonene",
     "yield_indoor": "450-550 g/m²", "is_autoflower": 0},
    {"name": "Cherry Pie", "breeder": "Cookie Fam", "strain_type": "Hybrid", "genetics": "Granddaddy Purple x Durban Poison",
     "flowering_weeks_min": 8, "flowering_weeks_max": 9, "thc_range": "16-24%", "difficulty": "Moderate",
     "description": "Sweet tart cherry. Dense buds. Balanced effects.", "terpenes": "Myrcene, Caryophyllene, Pinene",
     "yield_indoor": "400-450 g/m²", "is_autoflower": 0},
    {"name": "Forbidden Fruit", "breeder": "Chameleon Extracts", "strain_type": "Indica-dominant", "genetics": "Cherry Pie x Tangie",
     "flowering_weeks_min": 8, "flowering_weeks_max": 10, "thc_range": "21-26%", "difficulty": "Moderate",
     "description": "Tropical fruit/cherry/citrus. Dense purple nugs. Very relaxing.", "terpenes": "Myrcene, Limonene, Pinene",
     "yield_indoor": "400-500 g/m²", "is_autoflower": 0},
    {"name": "Headband", "breeder": "DNA Genetics", "strain_type": "Hybrid", "genetics": "OG Kush x Sour Diesel",
     "flowering_weeks_min": 9, "flowering_weeks_max": 10, "thc_range": "20-27%", "difficulty": "Moderate",
     "description": "Named for the pressure around your head. Creamy diesel.", "terpenes": "Myrcene, Limonene, Caryophyllene",
     "yield_indoor": "400-500 g/m²", "is_autoflower": 0},
    {"name": "Lemon Haze", "breeder": "Green House Seeds", "strain_type": "Sativa-dominant", "genetics": "Silver Haze x Lemon Skunk",
     "flowering_weeks_min": 8, "flowering_weeks_max": 10, "thc_range": "15-20%", "difficulty": "Moderate",
     "description": "Bright citrus. Uplifting clear-headed. Great for focus.", "terpenes": "Limonene, Terpinolene, Caryophyllene",
     "yield_indoor": "400-500 g/m²", "is_autoflower": 0},
    {"name": "Animal Mints", "breeder": "Seed Junky", "strain_type": "Hybrid", "genetics": "Animal Cookies x SinMint Cookies",
     "flowering_weeks_min": 8, "flowering_weeks_max": 9, "thc_range": "22-28%", "difficulty": "Moderate",
     "description": "Minty/gas/cookie dough. Dense frosty. Potent & balanced.", "terpenes": "Caryophyllene, Limonene, Myrcene",
     "yield_indoor": "400-500 g/m²", "is_autoflower": 0},
    {"name": "Slurricane", "breeder": "In House Genetics", "strain_type": "Indica-dominant", "genetics": "Do-Si-Dos x Purple Punch",
     "flowering_weeks_min": 8, "flowering_weeks_max": 9, "thc_range": "20-28%", "difficulty": "Moderate",
     "description": "Berry/grape/tropical. Beautiful purple colors. Strong indica.", "terpenes": "Myrcene, Limonene, Caryophyllene",
     "yield_indoor": "400-500 g/m²", "is_autoflower": 0},
    {"name": "MAC (Miracle Alien Cookies)", "breeder": "Capulator", "strain_type": "Hybrid", "genetics": "Alien Cookies F2 x Miracle 15",
     "flowering_weeks_min": 8, "flowering_weeks_max": 10, "thc_range": "20-23%", "difficulty": "Moderate",
     "description": "Creamy citrus. Fluffy frosty buds. Smooth uplifting high.", "terpenes": "Limonene, Caryophyllene, Myrcene",
     "yield_indoor": "400-500 g/m²", "is_autoflower": 0},
    {"name": "GG4 Auto", "breeder": "Various", "strain_type": "Hybrid", "genetics": "Gorilla Glue #4 x Ruderalis",
     "flowering_weeks_min": 8, "flowering_weeks_max": 10, "thc_range": "20-26%", "difficulty": "Easy",
     "description": "Auto version of the legendary GG4. Sticky and potent.", "terpenes": "Caryophyllene, Myrcene, Limonene",
     "yield_indoor": "400-500 g/m²", "is_autoflower": 1},

    # ─── Autoflower ────────────────────────────────────────────────────────
    {"name": "Northern Lights Auto", "breeder": "Royal Queen Seeds", "strain_type": "Indica", "genetics": "Northern Lights x Ruderalis",
     "flowering_weeks_min": 7, "flowering_weeks_max": 8, "thc_range": "14-18%", "difficulty": "Easy",
     "description": "Auto classic. 9-10wk seed to harvest. Forgiving.", "terpenes": "Myrcene, Pinene, Caryophyllene",
     "yield_indoor": "350-450 g/m²", "is_autoflower": 1},
    {"name": "Blue Dream Auto", "breeder": "Various", "strain_type": "Hybrid", "genetics": "Blue Dream x Ruderalis",
     "flowering_weeks_min": 8, "flowering_weeks_max": 10, "thc_range": "15-21%", "difficulty": "Easy",
     "description": "Auto version of the classic. Sweet berry. Great first grow.", "terpenes": "Myrcene, Caryophyllene, Pinene",
     "yield_indoor": "350-450 g/m²", "is_autoflower": 1},
    {"name": "Girl Scout Cookies Auto", "breeder": "FastBuds", "strain_type": "Hybrid", "genetics": "GSC x Ruderalis",
     "flowering_weeks_min": 8, "flowering_weeks_max": 9, "thc_range": "20-24%", "difficulty": "Easy",
     "description": "Fast auto. Cookies flavor. Surprisingly potent for auto.", "terpenes": "Caryophyllene, Limonene, Humulene",
     "yield_indoor": "350-450 g/m²", "is_autoflower": 1},
    {"name": "Amnesia Haze Auto", "breeder": "Royal Queen Seeds", "strain_type": "Sativa", "genetics": "Amnesia Haze x Ruderalis",
     "flowering_weeks_min": 8, "flowering_weeks_max": 10, "thc_range": "17-22%", "difficulty": "Easy",
     "description": "Auto sativa. Citrus haze. More manageable than the photo version.", "terpenes": "Terpinolene, Myrcene, Limonene",
     "yield_indoor": "350-450 g/m²", "is_autoflower": 1},
    {"name": "Zkittlez Auto", "breeder": "FastBuds", "strain_type": "Indica-dominant", "genetics": "Zkittlez x Ruderalis",
     "flowering_weeks_min": 8, "flowering_weeks_max": 9, "thc_range": "18-23%", "difficulty": "Easy",
     "description": "Candy terpenes in auto form. Colorful. 70-75 days total.", "terpenes": "Linalool, Caryophyllene, Humulene",
     "yield_indoor": "350-450 g/m²", "is_autoflower": 1},
    {"name": "Wedding Glue Auto", "breeder": "FastBuds", "strain_type": "Hybrid", "genetics": "Wedding Cake x Gorilla Glue Auto",
     "flowering_weeks_min": 9, "flowering_weeks_max": 10, "thc_range": "20-26%", "difficulty": "Easy",
     "description": "Potent auto hybrid. Sweet/earthy. Heavy resin production.", "terpenes": "Caryophyllene, Limonene, Myrcene",
     "yield_indoor": "400-500 g/m²", "is_autoflower": 1},
    {"name": "Purple Lemonade Auto", "breeder": "FastBuds", "strain_type": "Sativa-dominant", "genetics": "Unknown Purple x Citrus Auto",
     "flowering_weeks_min": 8, "flowering_weeks_max": 9, "thc_range": "18-22%", "difficulty": "Easy",
     "description": "Stunning purple. Tart citrus lemonade. Uplifting auto.", "terpenes": "Limonene, Myrcene, Caryophyllene",
     "yield_indoor": "350-450 g/m²", "is_autoflower": 1},
]

# ════════════════════════════════════════════════════════════════════════════
#  GLOSSARY
# ════════════════════════════════════════════════════════════════════════════

GLOSSARY = {
    "Autoflower": "Cannabis that flowers by age not light cycle, due to ruderalis genetics. 8-12 weeks seed to harvest.",
    "BX (Backcross)": "Crossing hybrid back to parent to reinforce traits.",
    "Cal-Mag": "Calcium-Magnesium supplement. Essential for LED/coco/RO water grows.",
    "Clone": "Genetic copy from a mother plant cutting. Identical genetics.",
    "Cola": "Main flower cluster at top of branch.",
    "Curing": "Post-harvest jar aging 2-8+ weeks. Develops flavor, smoothness.",
    "EC": "Electrical Conductivity — nutrient solution strength.",
    "F1": "First generation cross. Max hybrid vigor, wide variation.",
    "FIM": "Cut 80% of growth tip for 3-8 new branches. Less predictable than topping.",
    "Flush": "Plain water only 1-2 weeks before harvest.",
    "Keeper": "Exceptional phenotype preserved through cloning.",
    "LST": "Low Stress Training — bending/tying without cutting.",
    "Mainlining": "Symmetrical manifold of equal colas via repeated topping.",
    "Mother Plant": "Plant kept in veg permanently for taking clones.",
    "Node": "Point where branches/leaves emerge from stem.",
    "Phenotype": "Observable characteristics — how genotype expresses.",
    "Photoperiod": "Needs 12/12 light change to trigger flowering.",
    "PPFD": "Photosynthetic Photon Flux Density — usable light measurement.",
    "PPM": "Parts Per Million — nutrient concentration.",
    "SCROG": "Screen of Green — net for flat even canopy.",
    "Terpenes": "Aromatic compounds giving cannabis its smell/flavor/effects.",
    "Topping": "Cutting main tip to create two branches.",
    "Trichomes": "Resin glands producing cannabinoids and terpenes.",
    "VPD": "Vapor Pressure Deficit — temp/humidity relationship affecting transpiration.",
}
