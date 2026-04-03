# FILE: growforge/ai_assistant.py
"""
GrowForge AI — Complete self-contained cannabis cultivation expert system.

100% local. Zero external API calls. Zero internet. Zero LLM dependencies.

Architecture:
  1. Intent Classifier — fuzzy keyword/phrase scoring to understand what the user wants
  2. Entity Extractor — pulls nutrients, pests, symptoms, numbers, stages from text
  3. Symptom Diagnosis Engine — walks decision trees to score possible causes
  4. Data Analyzer — deep analysis of plant logs/env for proactive alerts
  5. Response Generator — builds personalized, context-aware natural language replies
  6. Conversation Memory — multi-turn context within a session
  7. Adaptive Learning — adjusts rule weights from user feedback
  8. Self-Coding Engine — generates new Python rule functions, validates, and hot-reloads them

The AI gets smarter over time through two mechanisms:
  (a) Weight adjustment: feedback shifts confidence scores on existing rules
  (b) Code generation: patterns in feedback trigger creation of new rule functions
      saved to learned_rules.py and hot-reloaded via importlib
"""

import os
import re
import json
import math
import sqlite3
import importlib
import threading
from datetime import datetime, timedelta
from difflib import SequenceMatcher, get_close_matches
from collections import Counter
from config import DB_NAME, BASE_DIR

from knowledge_base import (
    STAGE_GUIDE, NUTRIENT_ISSUES, PESTS, TRAINING_TECHNIQUES,
    CLONING_GUIDE, BREEDING_GUIDE, GLOSSARY, PH_LOCKOUT,
    SYMPTOM_PATTERNS, STRAIN_LIBRARY, VPD_ZONES,
    rule_weights, calc_vpd, ideal_rh_for_vpd,
    FEEDBACK_SCHEMA, RULE_TEMPLATES, validate_generated_code,
)

LEARNED_RULES_PATH = os.path.join(str(BASE_DIR), "learned_rules.py")

# ════════════════════════════════════════════════════════════════════════════
#  INTENT DEFINITIONS — keyword/phrase → intent mapping with weights
# ════════════════════════════════════════════════════════════════════════════

INTENTS = {
    "greeting":           (["hello","hi","hey","sup","howdy","yo"], ["how are you","what can you","help me","who are you"], 0.8),
    "stage_advice":       (["stage","germination","seedling","vegetative","veg","flowering","flower","bloom","flush","drying","curing"],
                           ["what stage","how long","when to flip","flip to flower","switch 12/12","ready to flower","light schedule","next stage","how many weeks"], 1.2),
    "symptom_diagnosis":  (["yellowing","yellow","brown","crispy","burnt","curling","curl","drooping","droop","wilting","spots","purple",
                            "pale","bleach","twisted","claw","clawing","necrosis","stretching","stunted","discolored","bronze","rusty","orange"],
                           ["leaves are","tips are","edges are","new growth","old leaves","lower leaves","what's wrong","why are my","help my plant","looks sick"], 1.5),
    "deficiency":         (["deficiency","deficient","nitrogen","phosphorus","potassium","calcium","magnesium","iron","zinc","manganese","sulfur","boron","cal-mag","calmag","epsom","lockout"],
                           ["nutrient problem","what deficiency","diagnose","not looking good"], 1.3),
    "pest_disease":       (["pest","bug","mite","mites","gnat","gnats","thrip","thrips","aphid","mold","mildew","botrytis","rot","fungus","webbing","larvae","flies","caterpillar"],
                           ["bugs on","something eating","white stuff","bud rot","root rot","tiny flies","webs on"], 1.4),
    "watering":           (["water","watering","overwater","underwater","dry","wet","moisture","runoff","drought"],
                           ["how often water","when to water","how much water","too much water","watering schedule","lift test"], 1.2),
    "nutrients_feeding":  (["nutrient","feed","feeding","fertilizer","nutes","npk","supplement","booster","pk","dose","dosage","strength","regiment","mix"],
                           ["how much feed","feeding schedule","what nutrients","nutrient burn","nute burn","when to feed","what to feed"], 1.2),
    "ph_ec":              (["ph","ec","ppm","tds","runoff"],
                           ["ph range","best ph","optimal ph","ph lockout","ph too high","ph too low","adjust ph","what should ph"], 1.3),
    "vpd":                (["vpd","vapor pressure","transpiration"],
                           ["what vpd","ideal vpd","vpd target","calculate vpd","vpd chart","vpd too"], 1.3),
    "temp_humidity":      (["temperature","temp","humidity","rh","hot","cold","heat","warm","freeze","climate","environment"],
                           ["ideal temp","too hot","too cold","raise humidity","lower humidity","night temp"], 1.1),
    "lighting":           (["light","lighting","led","hps","cfl","watt","ppfd","par","lux","spectrum","distance","intensity"],
                           ["light schedule","how far","light distance","how much light","light burn","18/6","12/12","24/0","20/4"], 1.1),
    "training":           (["lst","topping","topped","fim","scrog","supercrop","defoliate","defoliation","lollipop","mainline","manifold","train","training","bend","tie"],
                           ["how to top","when to top","should i top","low stress training","best training","train auto","should i defoliate"], 1.2),
    "harvest_timing":     (["harvest","chop","trichome","trichomes","amber","cloudy","milky","clear","pistil","ripe","mature"],
                           ["when to harvest","ready to harvest","time to chop","check trichomes","is it ready","weeks left"], 1.3),
    "cloning":            (["clone","cloning","clones","cutting","cuttings","mother","rooting","dome","propagation"],
                           ["how to clone","take cuttings","clone success","rooting hormone","mother plant","select mother","when to clone"], 1.2),
    "breeding":           (["breed","breeding","cross","crossing","pollen","pollinate","seed","seeds","male","female","sex","hermaphrodite","hermi",
                            "f1","f2","backcross","bx","pheno","phenotype","keeper","genetics","sts","feminized"],
                           ["how to breed","make seeds","cross strains","pheno hunt","select keeper","collect pollen","identify male","identify sex"], 1.2),
    "yield":              (["yield","grams","ounces","production","harvest weight"],
                           ["how much yield","increase yield","maximize yield","bigger buds","denser buds","more yield"], 1.0),
    "drying_curing":      (["dry","drying","cure","curing","jar","burp","burping","boveda","trim","trimming","hay smell"],
                           ["how to dry","how to cure","drying conditions","burp jars","hay smell","wet trim","dry trim","when to jar"], 1.2),
    "plant_checkup":      (["checkup","check","status","overview","summary","update"],
                           ["how is my plant","plant status","how's my grow","give me update","what should i do","next steps","any issues","doing well"], 1.1),
    "strain_info":        (["strain","cultivar","indica","sativa","hybrid","autoflower","photoperiod"],
                           ["best strain","recommend strain","strain info","flowering time","what strain"], 1.0),
    "glossary":           (["define","definition","meaning","explain","term"],
                           ["what is a","what does","explain what","tell me about"], 0.8),
}

# ════════════════════════════════════════════════════════════════════════════
#  CORE AI CLASS
# ════════════════════════════════════════════════════════════════════════════

class GrowForgeAI:
    """
    Complete self-contained cannabis cultivation AI.
    No external APIs. No internet. Pure Python expert system.
    """

    def __init__(self):
        self.memory = {}               # {plant_id: [(role, msg), ...]}
        self.global_memory = []        # for non-plant-specific chats
        self.topics_discussed = Counter()
        self.interaction_count = 0
        self.last_improvement = None
        self.rules_generated = 0
        self.learned_module = None     # dynamically loaded learned_rules module
        self._init_feedback_tables()
        self._load_learned_rules()
        self._load_saved_weights()

    # ────────────────────────────────────────────────────────────────────
    #  DATABASE INITIALIZATION
    # ────────────────────────────────────────────────────────────────────

    def _get_conn(self):
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_feedback_tables(self):
        """Create AI feedback and learning tables if they don't exist."""
        conn = self._get_conn()
        for sql in FEEDBACK_SCHEMA.values():
            try:
                conn.execute(sql)
            except Exception:
                pass
        conn.commit()
        conn.close()

    def _load_saved_weights(self):
        """Load persisted rule weights from database."""
        try:
            conn = self._get_conn()
            rows = conn.execute("SELECT rule_id, weight FROM ai_rule_weights").fetchall()
            conn.close()
            for row in rows:
                if row["rule_id"] in rule_weights:
                    rule_weights[row["rule_id"]] = row["weight"]
        except Exception:
            pass

    def _save_weights(self):
        """Persist current rule weights to database."""
        try:
            conn = self._get_conn()
            for rid, w in rule_weights.items():
                conn.execute(
                    "INSERT OR REPLACE INTO ai_rule_weights (rule_id, weight, last_adjusted) VALUES (?, ?, datetime('now'))",
                    (rid, w))
            conn.commit()
            conn.close()
        except Exception:
            pass

    # ────────────────────────────────────────────────────────────────────
    #  INTENT CLASSIFICATION
    # ────────────────────────────────────────────────────────────────────

    def _classify_intent(self, message):
        """Return sorted list of (intent, score) from message.

        Scoring:
          - Exact word match in keywords: +2.0
          - Substring match in keywords: +1.0
          - Fuzzy match (>80% similarity): +0.6
          - Phrase match: +3.0
          - Conversation continuity bonus: +1.5 if same topic as last turn
          - Multi-word query bonus: higher weight intent gets priority boost
        """
        msg = message.lower().strip()
        words = set(msg.split())
        scores = {}
        for intent, (keywords, phrases, weight) in INTENTS.items():
            score = 0.0
            for kw in keywords:
                if kw in words:
                    score += 2.0
                elif kw in msg:
                    score += 1.0
                else:
                    # Fuzzy match for typos (e.g., "yellowing" vs "yelowing")
                    for w in words:
                        if len(w) > 3 and len(kw) > 3:
                            if SequenceMatcher(None, kw, w).ratio() > 0.80:
                                score += 0.6
                                break
            for phrase in phrases:
                if phrase in msg:
                    score += 3.0
            scores[intent] = score * weight

        # Conversation continuity: boost the last topic slightly
        if self.topics_discussed:
            last_topic = self.topics_discussed.most_common(1)[0][0]
            if last_topic in scores and scores[last_topic] > 0:
                scores[last_topic] += 1.5

        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return [(n, s) for n, s in ranked if s > 0]

    # ────────────────────────────────────────────────────────────────────
    #  ENTITY EXTRACTION
    # ────────────────────────────────────────────────────────────────────

    def _extract_entities(self, message):
        """Pull structured entities from natural language."""
        msg = message.lower()
        ent = {"nutrients": [], "pests": [], "training": [], "stages": [],
               "symptoms": [], "leaf_loc": None, "numbers": {}}

        nut_map = {"nitrogen":"Nitrogen (N)", "phosphorus":"Phosphorus (P)", "potassium":"Potassium (K)",
                   "calcium":"Calcium (Ca)", "magnesium":"Magnesium (Mg)", "iron":"Iron (Fe)",
                   "zinc":"Zinc (Zn)", "manganese":"Manganese (Mn)", "sulfur":"Sulfur (S)",
                   "boron":"Boron (B)", "cal-mag":"Calcium (Ca)", "calmag":"Calcium (Ca)", "epsom":"Magnesium (Mg)"}
        for kw, n in nut_map.items():
            if kw in msg and n not in ent["nutrients"]:
                ent["nutrients"].append(n)

        pest_map = {"spider mite":"Spider Mites", "mite":"Spider Mites", "gnat":"Fungus Gnats",
                    "thrip":"Thrips", "aphid":"Aphids", "whitefl":"Whiteflies",
                    "powdery mildew":"Powdery Mildew", "mildew":"Powdery Mildew",
                    "bud rot":"Bud Rot (Botrytis)", "botrytis":"Bud Rot (Botrytis)", "root rot":"Root Rot"}
        for kw, p in pest_map.items():
            if kw in msg and p not in ent["pests"]:
                ent["pests"].append(p)

        for tech_name in TRAINING_TECHNIQUES:
            short = tech_name.split("(")[0].strip().lower()
            if short in msg or (len(short) > 3 and short[:4] in msg):
                ent["training"].append(tech_name)
        if "lst" in msg.split():
            ent["training"].append("LST (Low Stress Training)")

        for stage in STAGE_GUIDE:
            if stage.lower() in msg:
                ent["stages"].append(stage)
        if "veg" in msg.split():
            ent["stages"].append("Vegetative")
        if "flower" in msg.split() or "bloom" in msg:
            ent["stages"].append("Flowering")

        if any(w in msg for w in ["older","lower","bottom","old leaves"]):
            ent["leaf_loc"] = "older"
        elif any(w in msg for w in ["newer","upper","top","new growth","new leaves"]):
            ent["leaf_loc"] = "newer"

        symptom_kws = ["yellowing","yellow","brown spots","crispy","burnt tips","burnt edges",
                       "curling up","curling down","clawing","drooping","wilting","stretching",
                       "pale","purple","red stems","twisted","distorted","bleached","spots",
                       "slow growth","stunted","webbing","mold","powder",
                       "brown tips","leaf curl","taco","tacoing","foxtail","foxtailing",
                       "necrosis","chlorosis","interveinal","rust","rusty",
                       "mushy","slimy","fuzzy","gray mold","white powder",
                       "dry edges","crinkly","thin leaves","dark green",
                       "light burn","heat stress","wind burn","nutrient burn",
                       "orange spots","bronze","canoeing","hooking"]
        for s in symptom_kws:
            if s in msg:
                ent["symptoms"].append(s)

        # Extract numbers with more flexible patterns
        ph = re.search(r'ph\s*(?:of|is|at|=|:)?\s*(\d+\.?\d*)', msg)
        if not ph:
            ph = re.search(r'(\d+\.\d+)\s*ph', msg)
        if ph: ent["numbers"]["ph"] = float(ph.group(1))

        ec = re.search(r'ec\s*(?:of|is|at|=|:)?\s*(\d+\.?\d*)', msg)
        if not ec:
            ec = re.search(r'(\d+\.\d+)\s*ec', msg)
        if ec: ent["numbers"]["ec"] = float(ec.group(1))

        ppm = re.search(r'(\d+)\s*ppm', msg)
        if ppm and "ec" not in ent["numbers"]:
            ent["numbers"]["ppm"] = int(ppm.group(1))
            ent["numbers"]["ec"] = round(int(ppm.group(1)) / 500, 2)

        temp = re.search(r'(\d+\.?\d*)\s*(?:°?[cf]|degrees?|celsius|fahrenheit)', msg)
        if temp:
            t = float(temp.group(1))
            # Auto-convert F to C if value looks like Fahrenheit
            if t > 50 and ('f' in msg[temp.end()-2:temp.end()+2].lower()
                          or 'fahrenheit' in msg):
                t = round((t - 32) * 5 / 9, 1)
            ent["numbers"]["temp"] = t

        rh = re.search(r'(\d+\.?\d*)\s*%\s*(?:rh|humidity)?', msg)
        if not rh:
            rh = re.search(r'(?:rh|humidity)\s*(?:of|is|at|=|:)?\s*(\d+\.?\d*)', msg)
        if rh: ent["numbers"]["rh"] = float(rh.group(1))

        wk = re.search(r'week\s*(\d+)', msg)
        if not wk:
            wk = re.search(r'wk\s*(\d+)', msg)
        if wk: ent["numbers"]["week"] = int(wk.group(1))

        day = re.search(r'day\s*(\d+)', msg)
        if day: ent["numbers"]["day"] = int(day.group(1))

        return ent

    # ────────────────────────────────────────────────────────────────────
    #  CONTEXT BUILDER — reads plant data from the database
    # ────────────────────────────────────────────────────────────────────

    def get_context(self, plant_id=None):
        """Build full context dict from database for a given plant (or global)."""
        ctx = {"plant": None, "events": [], "environment": None,
               "all_plants": [], "stats": {}}
        try:
            conn = self._get_conn()
            # All active plants
            rows = conn.execute("SELECT * FROM plants WHERE is_active=1 ORDER BY updated_at DESC").fetchall()
            ctx["all_plants"] = [dict(r) for r in rows]

            if plant_id:
                row = conn.execute("SELECT * FROM plants WHERE id=?", (plant_id,)).fetchone()
                if row:
                    ctx["plant"] = dict(row)
                    evts = conn.execute(
                        "SELECT * FROM events WHERE plant_id=? ORDER BY event_date DESC LIMIT 20",
                        (plant_id,)).fetchall()
                    ctx["events"] = [dict(e) for e in evts]
                    if ctx["plant"].get("environment_id"):
                        env = conn.execute("SELECT * FROM environments WHERE id=?",
                                           (ctx["plant"]["environment_id"],)).fetchone()
                        if env:
                            ctx["environment"] = dict(env)
            # Stats
            ctx["stats"]["active"] = conn.execute("SELECT COUNT(*) FROM plants WHERE is_active=1").fetchone()[0]
            ctx["stats"]["harvested"] = conn.execute("SELECT COUNT(*) FROM plants WHERE stage='Harvested'").fetchone()[0]
            ctx["stats"]["events"] = conn.execute("SELECT COUNT(*) FROM events").fetchone()[0]
            ctx["stats"]["total_yield"] = conn.execute("SELECT COALESCE(SUM(yield_grams),0) FROM plants WHERE stage='Harvested'").fetchone()[0]
            conn.close()
        except Exception:
            pass
        return ctx

    # ────────────────────────────────────────────────────────────────────
    #  SYMPTOM DIAGNOSIS ENGINE
    # ────────────────────────────────────────────────────────────────────

    def analyze_symptoms(self, symptoms_list, leaf_loc=None, medium="", ph=None, stage=""):
        """
        Walk the symptom pattern database and score possible diagnoses.
        Returns sorted list of (diagnosis, confidence, fix, note).

        Scoring factors:
          - Keyword match: +1.5 (exact), +0.8 (fuzzy >75%)
          - Pattern descriptor match: +1.0
          - Leaf location: +2.0 (correct), -1.0 (wrong)
          - pH lockout context: x1.3 boost for micronutrient lockout
          - Stage context: suppresses expected deficiencies
          - Medium context: adjusts for soil vs hydro differences
          - Multi-symptom bonus: compounds when 3+ symptoms match
        """
        results = []
        symptoms_str = " ".join(str(s) for s in symptoms_list).lower()
        is_hydro = any(w in medium.lower() for w in ["coco", "hydro", "dwc", "perlite", "rock"]) if medium else False

        for pattern in SYMPTOM_PATTERNS:
            score = 0.0
            matched_kws = 0
            # Match symptom keywords
            for kw in pattern["keywords"]:
                for sym in symptoms_list:
                    if kw in sym:
                        score += 1.5
                        matched_kws += 1
                        break
                    elif SequenceMatcher(None, kw, sym).ratio() > 0.75:
                        score += 0.8
                        matched_kws += 1
                        break

            # Match pattern descriptors
            for p in pattern.get("patterns", []):
                for sym in symptoms_list:
                    if p in sym:
                        score += 1.0

            # Multi-symptom confidence bonus
            if matched_kws >= 3:
                score *= 1.3
            elif matched_kws >= 2:
                score *= 1.1

            # Leaf location bonus
            ploc = pattern.get("leaf_loc", "any")
            if leaf_loc and ploc != "any":
                if leaf_loc == ploc:
                    score += 2.0
                else:
                    score -= 1.0

            if score <= 0:
                continue

            # Apply rule weight
            rid = pattern.get("rule_id", "")
            weight = rule_weights.get(rid, 1.0)
            base_conf = pattern.get("confidence", 0.5)
            final_conf = min(0.99, base_conf * weight * (score / 3.0))

            # pH context adjustment — broader lockout detection
            if ph is not None:
                threshold = 6.0 if is_hydro else 6.5
                if rid in ("iron_def", "manganese_def", "zinc_def"):
                    if ph > threshold:
                        final_conf = min(0.99, final_conf * 1.3)
                elif rid in ("calcium_def", "magnesium_def"):
                    if is_hydro and ph < 5.5:
                        final_conf = min(0.99, final_conf * 1.25)
                    elif not is_hydro and ph < 6.0:
                        final_conf = min(0.99, final_conf * 1.25)
                # General pH lockout detection
                if rid == "ph_lockout":
                    if ph < 5.5 or ph > 7.2:
                        final_conf = min(0.99, final_conf * 1.4)

            # Stage context — N deficiency normal in late flower/flush
            if rid == "nitrogen_def" and stage in ("Flushing", "Drying", "Harvested"):
                final_conf *= 0.3  # suppress — expected

            # Overwatering more likely for seedlings
            if rid == "overwater" and stage in ("Seedling", "Germination"):
                final_conf = min(0.99, final_conf * 1.2)

            # Medium-specific adjustments
            if is_hydro and rid == "ph_lockout":
                final_conf = min(0.99, final_conf * 1.15)

            results.append({
                "diagnosis": pattern["diagnosis"],
                "confidence": round(final_conf, 2),
                "fix": pattern.get("fix", ""),
                "note": pattern.get("note", ""),
                "rule_id": rid,
            })

        # Also check learned rules
        if self.learned_module:
            for name in dir(self.learned_module):
                if name.startswith("rule_") and "symptom" in name:
                    try:
                        fn = getattr(self.learned_module, name)
                        diag, score = fn(symptoms_list, leaf_loc, medium, ph, stage)
                        if score > 0.1:
                            results.append({"diagnosis": diag, "confidence": round(score, 2),
                                            "fix": "", "note": f"(learned rule: {name})", "rule_id": name})
                    except Exception:
                        pass

        results.sort(key=lambda x: x["confidence"], reverse=True)
        return results[:5]

    # ────────────────────────────────────────────────────────────────────
    #  IMAGE DESCRIPTION TRIAGE
    # ────────────────────────────────────────────────────────────────────

    def triage_description(self, description):
        """Analyze a text description of a photo and suggest diagnoses."""
        desc = description.lower()
        symptoms = []
        # Extract symptoms from description — expanded keyword set
        symptom_kws = [
            "yellow", "brown", "spots", "crispy", "burnt", "curling", "drooping",
            "wilting", "purple", "red", "pale", "twisted", "webbing", "mold",
            "powder", "fuzzy", "gray", "flies", "bugs", "stretching", "stunted",
            "claw", "necrosis", "bronze", "rusty", "bleach", "white", "orange",
            "slimy", "mushy", "dry", "thin", "holes", "sticky", "shiny",
            "foxtail", "taco", "canoe", "wrinkle", "limp", "discolor",
        ]
        for kw in symptom_kws:
            if kw in desc:
                symptoms.append(kw)

        leaf_loc = None
        if any(w in desc for w in ["older", "lower", "bottom", "fan leaves"]):
            leaf_loc = "older"
        elif any(w in desc for w in ["newer", "upper", "top", "new growth", "tips"]):
            leaf_loc = "newer"

        # Extract pH if mentioned
        ph = None
        ph_match = re.search(r'ph\s*(\d+\.?\d*)', desc)
        if ph_match:
            ph = float(ph_match.group(1))

        # Extract medium
        medium = ""
        if any(w in desc for w in ["coco", "hydro", "dwc"]):
            medium = "coco"
        elif any(w in desc for w in ["soil", "organic"]):
            medium = "soil"

        # Extract stage
        stage = ""
        for s in ["seedling", "veg", "vegetative", "flower", "flowering", "bloom"]:
            if s in desc:
                stage = s.capitalize()
                if stage == "Veg":
                    stage = "Vegetative"
                elif stage == "Bloom":
                    stage = "Flowering"
                break

        if not symptoms:
            return ("I'd need more details about what you're seeing. Describe the color changes, "
                    "which leaves are affected (upper new growth vs lower older leaves), "
                    "any spots, curling, or unusual textures. That helps me narrow it down.")

        results = self.analyze_symptoms(symptoms, leaf_loc, medium, ph, stage)
        if not results:
            return "I couldn't match those symptoms to a specific issue. Try the Deficiency Wizard for a step-by-step diagnosis."

        resp = "📸 **Photo Analysis**\n\n"
        resp += "Based on your description, here's what I'm seeing:\n\n"
        for i, r in enumerate(results[:3]):
            pct = int(r["confidence"] * 100)
            resp += f"**{i+1}. {r['diagnosis']}** — {pct}% confidence\n"
            if r["fix"]:
                resp += f"   ✅ {r['fix']}\n"
            if r["note"]:
                resp += f"   💡 {r['note']}\n"
            resp += "\n"

        resp += "**Always check pH first** — it's the #1 cause of nutrient issues."
        if leaf_loc is None:
            resp += "\n\n💡 Tip: mentioning if it's on *older/lower* or *newer/upper* leaves helps me be more accurate."
        return resp

    # ────────────────────────────────────────────────────────────────────
    #  PROACTIVE ALERTS — scans data for issues
    # ────────────────────────────────────────────────────────────────────

    def proactive_alerts(self, context):
        """Analyze plant data and return list of alert dicts."""
        alerts = []
        plant = context.get("plant")
        events = context.get("events", [])
        env = context.get("environment")
        if not plant:
            return alerts

        now = datetime.now()
        stage = plant.get("stage", "")

        # Days tracking
        def days_since(date_str):
            if not date_str: return None
            try:
                return (now - datetime.strptime(str(date_str)[:10], "%Y-%m-%d")).days
            except (ValueError, TypeError): return None

        ds_start = days_since(plant.get("start_date"))
        ds_flower = days_since(plant.get("flower_date"))

        # Stage overstay
        if stage in STAGE_GUIDE and ds_start:
            max_d = STAGE_GUIDE[stage]["duration_days"][1]
            if max_d and ds_start > max_d * 1.3 and stage not in ("Harvested","Curing"):
                alerts.append({"type": "warning", "plant": plant["name"],
                    "message": f"Been in {stage} for {ds_start}d (typical max {max_d}d). Consider advancing."})

        # Watering check
        water_evts = [e for e in events if e.get("event_type") in ("Watering","Feeding")]
        if water_evts:
            dw = days_since(water_evts[0].get("event_date"))
            if dw and dw >= 4:
                alerts.append({"type": "warning", "plant": plant["name"],
                    "message": f"No watering/feeding logged in {dw} days. Check soil moisture."})
        elif events:
            alerts.append({"type": "info", "plant": plant["name"],
                "message": "No watering events logged yet. Log waterings for better tracking."})

        # pH analysis
        ph_evts = [e for e in events if e.get("ph") is not None]
        if ph_evts:
            recent_ph = [e["ph"] for e in ph_evts[:5]]
            avg_ph = sum(recent_ph) / len(recent_ph)
            medium = plant.get("medium", "") or (env.get("medium","") if env else "")
            is_hydro = any(w in medium.lower() for w in ["coco","hydro","dwc","perlite","rock"])
            lo, hi = (5.5, 6.5) if is_hydro else (6.0, 6.8)
            if avg_ph < lo:
                alerts.append({"type": "warning", "plant": plant["name"],
                    "message": f"pH averaging {avg_ph:.1f} — below optimal ({lo}-{hi}). Risk of Ca/Mg/P lockout."})
            elif avg_ph > hi:
                alerts.append({"type": "warning", "plant": plant["name"],
                    "message": f"pH averaging {avg_ph:.1f} — above optimal ({lo}-{hi}). Risk of Fe/Mn/Zn lockout."})
            if len(recent_ph) >= 3 and max(recent_ph) - min(recent_ph) > 1.0:
                alerts.append({"type": "info", "plant": plant["name"],
                    "message": f"pH swinging ({min(recent_ph):.1f} to {max(recent_ph):.1f}). Try to be more consistent."})

        # VPD check
        env_evts = [e for e in events if e.get("temp") and e.get("humidity")]
        if env_evts and stage in STAGE_GUIDE:
            last = env_evts[0]
            vpd = calc_vpd(last["temp"], last["humidity"])
            vpd_target = STAGE_GUIDE[stage].get("vpd_target")
            if vpd_target:
                if vpd < vpd_target[0] - 0.2:
                    rh_ideal = ideal_rh_for_vpd(last["temp"], vpd_target[0])
                    alerts.append({"type": "info", "plant": plant["name"],
                        "message": f"VPD {vpd:.2f} kPa — low for {stage} (target {vpd_target[0]}-{vpd_target[1]}). Try RH ~{rh_ideal:.0f}%."})
                elif vpd > vpd_target[1] + 0.2:
                    rh_ideal = ideal_rh_for_vpd(last["temp"], vpd_target[1])
                    alerts.append({"type": "warning", "plant": plant["name"],
                        "message": f"VPD {vpd:.2f} kPa — high for {stage} (target {vpd_target[0]}-{vpd_target[1]}). Try RH ~{rh_ideal:.0f}%."})

        # Flowering timeline
        if stage == "Flowering" and ds_flower:
            strain = plant.get("strain_name", "")
            fw = ds_flower // 7
            for s in STRAIN_LIBRARY:
                if s["name"].lower() in strain.lower():
                    if fw >= s["flowering_weeks_min"] - 1:
                        alerts.append({"type": "info", "plant": plant["name"],
                            "message": f"Flower week {fw} — {strain} typically finishes wk {s['flowering_weeks_min']}-{s['flowering_weeks_max']}. Start checking trichomes!"})
                    break

        # Veg readiness for photoperiod
        if stage == "Vegetative" and plant.get("plant_type") == "Photoperiod":
            dv = days_since(plant.get("veg_date"))
            if dv and dv >= 42:
                alerts.append({"type": "info", "plant": plant["name"],
                    "message": f"Vegging for {dv//7} weeks. Ready to flip to flower whenever you choose."})

        # EC monitoring
        ec_evts = [e for e in events if e.get("ec") is not None]
        if ec_evts and len(ec_evts) >= 2:
            recent_ec = [e["ec"] for e in ec_evts[:5]]
            avg_ec = sum(recent_ec) / len(recent_ec)
            if stage in ("Seedling", "Germination") and avg_ec > 0.8:
                alerts.append({"type": "warning", "plant": plant["name"],
                    "message": f"EC averaging {avg_ec:.1f} — too high for {stage}. Seedlings need EC 0.2-0.6."})
            elif stage == "Flowering" and avg_ec < 0.8:
                alerts.append({"type": "info", "plant": plant["name"],
                    "message": f"EC averaging {avg_ec:.1f} — consider increasing nutrients in flower (target EC 1.2-2.0)."})

        # Stale data warning — no events logged recently
        if events:
            last_event_days = days_since(events[0].get("event_date"))
            if last_event_days and last_event_days >= 7 and stage not in ("Harvested", "Curing"):
                alerts.append({"type": "info", "plant": plant["name"],
                    "message": f"No events logged in {last_event_days} days. Log observations to get better AI recommendations."})

        # Check learned rules for custom alerts
        if self.learned_module:
            for name in dir(self.learned_module):
                if name.startswith("rule_") and "alert" in name:
                    try:
                        fn = getattr(self.learned_module, name)
                        new_alerts = fn(plant, events, env)
                        alerts.extend(new_alerts)
                    except Exception:
                        pass

        return alerts

    # ────────────────────────────────────────────────────────────────────
    #  STAGE GUIDANCE
    # ────────────────────────────────────────────────────────────────────

    def stage_guidance(self, stage, plant_type="Photoperiod"):
        """Return formatted stage guidance string."""
        if stage not in STAGE_GUIDE:
            close = get_close_matches(stage, STAGE_GUIDE.keys(), n=1, cutoff=0.5)
            if close:
                stage = close[0]
            else:
                return f"I don't have info on stage '{stage}'. Known stages: {', '.join(STAGE_GUIDE.keys())}"

        g = STAGE_GUIDE[stage]
        is_auto = "auto" in plant_type.lower()
        light = g.get("light_hours_auto") if is_auto else g.get("light_hours_photo")

        resp = f"🌱 **{stage} Stage Guide** ({'Auto' if is_auto else 'Photo'})\n\n"
        resp += f"📅 Duration: {g['duration']}\n"
        if g.get("temp_range"):
            resp += f"🌡️ Temp: {g['temp_range'][0]}-{g['temp_range'][1]}°C\n"
        if g.get("rh_range"):
            resp += f"💧 RH: {g['rh_range'][0]}-{g['rh_range'][1]}%\n"
        if g.get("vpd_target"):
            resp += f"📊 VPD: {g['vpd_target'][0]}-{g['vpd_target'][1]} kPa\n"
        resp += f"💡 Light: {light}\n"
        resp += f"☀️ PPFD: {g['ppfd'][0]}-{g['ppfd'][1]} µmol/m²/s\n"
        if g.get("nutrient_needs"):
            resp += f"🧪 Nutrients: {g['nutrient_needs']}\n"
        resp += f"\n{g['description']}\n"

        if g.get("checklist"):
            resp += "\n**Checklist:**\n"
            for item in g["checklist"]:
                resp += f"  ☐ {item}\n"

        if g.get("sub_stages"):
            resp += "\n**Sub-stages:**\n"
            for sub, data in g["sub_stages"].items():
                resp += f"\n  🔸 {sub}: VPD {data['vpd'][0]}-{data['vpd'][1]}, RH {data['rh'][0]}-{data['rh'][1]}%\n"
                resp += f"    {data['notes']}\n"

        if g.get("transition_signs"):
            resp += "\n**Ready for next stage when:**\n"
            for sign in g["transition_signs"]:
                resp += f"  ✓ {sign}\n"

        if g.get("common_issues"):
            resp += "\n**Common Issues:**\n"
            for issue, fix in g["common_issues"]:
                resp += f"  ⚠️ {issue}\n     → {fix}\n"

        return resp

    # ────────────────────────────────────────────────────────────────────
    #  CLONING ADVICE
    # ────────────────────────────────────────────────────────────────────

    def cloning_advice(self, topic=None):
        """Return cloning guidance. Topic can narrow the response."""
        if topic:
            topic_l = topic.lower()
            for key, data in CLONING_GUIDE.items():
                if key == "success_factors":
                    continue
                if any(w in topic_l for w in key.split("_")):
                    resp = f"🧬 **{data['title']}**\n\n"
                    for tip in data["tips"]:
                        resp += f"  • {tip}\n"
                    return resp

        # General overview
        resp = "🧬 **Cloning Guide**\n\n"
        for key, data in CLONING_GUIDE.items():
            if key == "success_factors":
                continue
            resp += f"**{data['title']}:**\n"
            for tip in data["tips"][:4]:
                resp += f"  • {tip}\n"
            resp += "\n"

        sf = CLONING_GUIDE.get("success_factors", {})
        if sf.get("method_success_rates"):
            resp += "**Success Rates by Method:**\n"
            for method, rate in sf["method_success_rates"].items():
                resp += f"  • {method}: ~{int(rate*100)}%\n"

        return resp

    # ────────────────────────────────────────────────────────────────────
    #  BREEDING ADVICE
    # ────────────────────────────────────────────────────────────────────

    def breeding_advice(self, topic=None):
        """Return breeding guidance."""
        if topic:
            topic_l = topic.lower()
            # Generation lookup
            gen_guide = BREEDING_GUIDE.get("generation_guide", {})
            for gen, desc in gen_guide.items():
                if gen.lower() in topic_l:
                    return f"🔬 **{gen} Generation**\n\n{desc}"

            # Sex identification
            if any(w in topic_l for w in ["sex","male","female","identify","hermie","hermi"]):
                si = BREEDING_GUIDE.get("sex_identification", {})
                resp = "🔬 **Sex Identification**\n\n"
                resp += "**Male Signs:**\n" + "".join(f"  • {s}\n" for s in si.get("male_signs", []))
                resp += "\n**Female Signs:**\n" + "".join(f"  • {s}\n" for s in si.get("female_signs", []))
                resp += "\n**Hermie Signs:**\n" + "".join(f"  • {s}\n" for s in si.get("hermie_signs", []))
                return resp

            for key, data in BREEDING_GUIDE.items():
                if isinstance(data, dict) and "title" in data:
                    if any(w in topic_l for w in key.split("_")):
                        resp = f"🔬 **{data['title']}**\n\n"
                        for item in data.get("content", data.get("tips", [])):
                            resp += f"  • {item}\n"
                        return resp

        # General
        resp = "🔬 **Breeding Guide**\n\n"
        for key, data in BREEDING_GUIDE.items():
            if isinstance(data, dict) and "title" in data:
                resp += f"**{data['title']}:**\n"
                for item in (data.get("content", data.get("tips", [])))[:3]:
                    resp += f"  • {item}\n"
                resp += "\n"
        resp += "**Generations:** " + ", ".join(BREEDING_GUIDE.get("generation_guide", {}).keys())
        return resp

    # ────────────────────────────────────────────────────────────────────
    #  SUGGEST NEXT ACTION
    # ────────────────────────────────────────────────────────────────────

    def suggest_next_action(self, context):
        """Based on plant data, suggest the most important next action."""
        plant = context.get("plant")
        if not plant:
            return "Add a plant to get personalized next-action suggestions!"

        stage = plant.get("stage", "")
        is_auto = "auto" in str(plant.get("plant_type", "")).lower()
        events = context.get("events", [])

        def days_since(d):
            if not d: return None
            try: return (datetime.now() - datetime.strptime(str(d)[:10], "%Y-%m-%d")).days
            except (ValueError, TypeError): return None

        suggestions = []

        # Stage-specific
        if stage == "Germination":
            suggestions.append("Watch for taproot emergence. Once 0.5-1 inch, plant taproot-down in moist medium.")
        elif stage == "Seedling":
            ds = days_since(plant.get("start_date"))
            if ds and ds > 14:
                suggestions.append("If you have 3-4 sets of true leaves, it's time to advance to Vegetative stage.")
            else:
                suggestions.append("Keep humidity high (60-70%), light gentle (200-400 PPFD). No nutrients until 2nd set of true leaves.")
        elif stage == "Vegetative":
            ds = days_since(plant.get("veg_date"))
            if ds and ds < 14:
                suggestions.append("Early veg — focus on building a strong root system. Don't overwater.")
            elif ds and ds >= 28 and not is_auto:
                suggestions.append("Consider whether you're ready to flip to flower. Take clones first if you want to preserve genetics!")
            else:
                suggestions.append("Good time for training (LST, topping after node 4-5). Gradually increase nutrients.")
            if not is_auto:
                suggestions.append("Tip: take clones BEFORE flipping to flower — you can't go back once she's flowering.")
        elif stage == "Flowering":
            fw = days_since(plant.get("flower_date"))
            if fw:
                wk = fw // 7
                if wk <= 2:
                    suggestions.append("Stretch phase! Plant may double in height. Last chance for training. Watch for males.")
                elif wk <= 6:
                    suggestions.append(f"Flower week {wk} — bud formation. Add PK booster. Support heavy branches.")
                else:
                    suggestions.append(f"Flower week {wk} — start checking trichomes daily with a loupe. Plan your flush.")
        elif stage == "Flushing":
            suggestions.append("Plain water only. Check trichomes daily: target 80-90% cloudy + 10-20% amber. Prepare drying space.")
        elif stage == "Drying":
            suggestions.append("Check daily: stems should snap not bend. Target 60°F / 60% RH. Darkness. No fans on buds.")
        elif stage == "Curing":
            suggestions.append("Burp jars daily for 2 weeks, then weekly. Target 58-62% RH in jars. Patience = quality.")

        # Check if watering is overdue
        water_evts = [e for e in events if e.get("event_type") in ("Watering", "Feeding")]
        if water_evts:
            dw = days_since(water_evts[0].get("event_date"))
            if dw and dw >= 3 and stage not in ("Drying", "Curing", "Harvested"):
                suggestions.insert(0, f"⚠️ Last watering was {dw} days ago — check if plant needs water (lift test).")

        return "\n".join(f"→ {s}" for s in suggestions) if suggestions else "Everything looks good! Keep doing what you're doing."

    # ────────────────────────────────────────────────────────────────────
    #  MAIN CHAT RESPONSE — the primary entry point
    # ────────────────────────────────────────────────────────────────────

    def chat_response(self, message, plant_id=None):
        """
        Main chat entry point. Classifies intent, extracts entities,
        builds context, and generates a personalized response.
        Returns (response_text, confidence_float).
        """
        self.interaction_count += 1
        ctx = self.get_context(plant_id)
        intents = self._classify_intent(message)
        entities = self._extract_entities(message)
        plant = ctx.get("plant")

        # Store in memory
        mem_key = plant_id or "global"
        if mem_key not in self.memory:
            self.memory[mem_key] = []
        self.memory[mem_key].append(("user", message))

        # Track topics
        if intents:
            self.topics_discussed[intents[0][0]] += 1

        top_intent = intents[0][0] if intents else "greeting"
        confidence = 0.75

        # Check for follow-up: short messages that refer to prior context
        if len(message.split()) <= 4 and mem_key in self.memory and len(self.memory[mem_key]) >= 2:
            prev_msgs = self.memory[mem_key]
            followup_words = {"yes","yeah","yep","no","nope","more","explain","why",
                              "how","what else","details","continue","go on","and"}
            if any(w in message.lower() for w in followup_words):
                # Carry forward entities from the last exchange
                for prev_role, prev_msg in reversed(self.memory[mem_key][:-1]):
                    if prev_role == "user":
                        prev_entities = self._extract_entities(prev_msg)
                        # Merge previous entities into current
                        for key in ("nutrients","pests","training","stages","symptoms"):
                            if not entities.get(key) and prev_entities.get(key):
                                entities[key] = prev_entities[key]
                        if not entities.get("leaf_loc") and prev_entities.get("leaf_loc"):
                            entities["leaf_loc"] = prev_entities["leaf_loc"]
                        for nk, nv in prev_entities.get("numbers", {}).items():
                            if nk not in entities["numbers"]:
                                entities["numbers"][nk] = nv
                        break

        # ── Route to handler based on intent ──────────────────────────
        if top_intent == "greeting":
            resp = self._handle_greeting(ctx)
            confidence = 0.95

        elif top_intent == "symptom_diagnosis":
            resp, confidence = self._handle_symptoms(entities, ctx)

        elif top_intent == "deficiency":
            resp, confidence = self._handle_deficiency(entities, ctx)

        elif top_intent == "pest_disease":
            resp, confidence = self._handle_pest(entities, ctx)

        elif top_intent == "stage_advice":
            resp = self._handle_stage(entities, ctx)
            confidence = 0.88

        elif top_intent == "watering":
            resp = self._handle_watering(ctx)
            confidence = 0.85

        elif top_intent == "nutrients_feeding":
            resp = self._handle_nutrients(entities, ctx)
            confidence = 0.82

        elif top_intent == "ph_ec":
            resp = self._handle_ph_ec(entities, ctx)
            confidence = 0.87

        elif top_intent == "vpd":
            resp = self._handle_vpd(entities, ctx)
            confidence = 0.88

        elif top_intent == "temp_humidity":
            resp = self._handle_temp_rh(entities, ctx)
            confidence = 0.84

        elif top_intent == "lighting":
            resp = self._handle_lighting(entities, ctx)
            confidence = 0.83

        elif top_intent == "training":
            resp = self._handle_training(entities, ctx)
            confidence = 0.86

        elif top_intent == "harvest_timing":
            resp = self._handle_harvest(ctx)
            confidence = 0.87

        elif top_intent == "cloning":
            resp = self.cloning_advice(message)
            confidence = 0.85

        elif top_intent == "breeding":
            resp = self.breeding_advice(message)
            confidence = 0.84

        elif top_intent == "yield":
            resp = self._handle_yield(ctx)
            confidence = 0.72

        elif top_intent == "drying_curing":
            stage_q = "Drying" if "dry" in message.lower() else "Curing"
            resp = self.stage_guidance(stage_q)
            confidence = 0.87

        elif top_intent == "plant_checkup":
            resp = self._handle_checkup(ctx)
            confidence = 0.85

        elif top_intent == "strain_info":
            resp = self._handle_strain(entities, message)
            confidence = 0.80

        elif top_intent == "glossary":
            resp = self._handle_glossary(message)
            confidence = 0.90

        else:
            resp = self._handle_fallback(message, ctx)
            confidence = 0.60

        # Store bot response
        self.memory[mem_key].append(("bot", resp))

        # Auto-improve periodically
        if self.interaction_count % 10 == 0:
            threading.Thread(target=self.auto_improve, daemon=True).start()

        return resp, round(confidence, 2)

    # ────────────────────────────────────────────────────────────────────
    #  INTENT HANDLERS — each generates a focused response
    # ────────────────────────────────────────────────────────────────────

    def _handle_greeting(self, ctx):
        plant_count = len(ctx.get("all_plants", []))
        greeting = "👋 **Hey! I'm GrowForge AI** — your local grow coach.\n\n"
        if plant_count > 0:
            greeting += f"You've got {plant_count} active plant(s). "
            greeting += "Select a plant from the dropdown for personalized advice, or ask me anything:\n\n"
        else:
            greeting += "Looks like you haven't added any plants yet. Head to the Plants tab to start!\n\nMeanwhile, I can help with:\n\n"
        greeting += ("  🌱 Stage guidance & checklists\n  🧪 Nutrient deficiency diagnosis\n"
                     "  🐛 Pest identification & treatment\n  ✂️ Training techniques (LST, topping, SCROG...)\n"
                     "  📊 VPD, pH, and environment optimization\n  🧬 Cloning & breeding advice\n"
                     "  🌾 Harvest timing\n  📖 Cannabis glossary\n\n"
                     "Just describe what you're seeing or ask a question!")
        return greeting

    def _handle_symptoms(self, entities, ctx):
        symptoms = entities.get("symptoms", [])
        leaf_loc = entities.get("leaf_loc")
        plant = ctx.get("plant")
        ph = entities["numbers"].get("ph")
        medium = ""
        stage = ""
        if plant:
            medium = plant.get("medium", "")
            stage = plant.get("stage", "")
            # Try to get pH from recent events if not in message
            if ph is None:
                for e in ctx.get("events", []):
                    if e.get("ph"):
                        ph = e["ph"]
                        break

        if not symptoms:
            return ("Tell me more about what you're seeing. Which leaves are affected (upper new growth or lower "
                    "older leaves)? What color changes? Any spots, curling, or crispy edges?"), 0.50

        results = self.analyze_symptoms(symptoms, leaf_loc, medium, ph, stage)
        if not results:
            return "I couldn't match those symptoms to a specific issue. Could you describe in more detail?", 0.45

        resp = "🔍 **Symptom Analysis**\n\n"
        # Add context if we have plant
        if plant:
            resp += f"For **{plant['name']}** ({stage}"
            if ph:
                resp += f", pH {ph}"
            resp += "):\n\n"

        for i, r in enumerate(results[:3]):
            pct = int(r["confidence"] * 100)
            resp += f"**{i+1}. {r['diagnosis']}** — {pct}% confidence\n"
            if r["fix"]:
                resp += f"   ✅ {r['fix']}\n"
            if r["note"]:
                resp += f"   💡 {r['note']}\n"
            resp += "\n"

        resp += "**Always check pH first** — it's the root cause of most nutrient issues."
        if leaf_loc is None:
            resp += "\n\n💡 Tip: telling me if it's on *older/lower* or *newer/upper* leaves would help me be more accurate."

        return resp, results[0]["confidence"]

    def _handle_deficiency(self, entities, ctx):
        nutrients = entities.get("nutrients", [])
        if nutrients:
            resp = ""
            for nut_name in nutrients[:2]:
                if nut_name in NUTRIENT_ISSUES:
                    data = NUTRIENT_ISSUES[nut_name]
                    mobile = "Mobile ↓ (older leaves first)" if data["mobile"] else "Immobile ↑ (new growth first)"
                    resp += f"🧪 **{nut_name}** — {mobile}\n\n"
                    d = data.get("deficiency", {})
                    resp += "**Deficiency Symptoms:**\n"
                    for s in d.get("symptoms", []):
                        resp += f"  • {s}\n"
                    resp += "\n**Fix:**\n"
                    for f in d.get("fix", []):
                        resp += f"  ✅ {f}\n"
                    if d.get("notes"):
                        resp += f"\n💡 {d['notes']}\n"
                    t = data.get("toxicity", {})
                    if t:
                        resp += f"\n**Toxicity Symptoms:** {', '.join(t.get('symptoms',['N/A']))}\n"
                    resp += "\n"
            return resp, 0.88
        return ("Which nutrient are you asking about? I know: Nitrogen, Phosphorus, Potassium, "
                "Calcium, Magnesium, Iron, Zinc, Manganese, Sulfur, Boron."), 0.55

    def _handle_pest(self, entities, ctx):
        pests = entities.get("pests", [])
        if pests:
            resp = ""
            for pest_name in pests[:2]:
                if pest_name in PESTS:
                    data = PESTS[pest_name]
                    resp += f"🐛 **{pest_name}** — Severity: {data['severity']}\n\n"
                    resp += "**Signs:**\n"
                    for s in data["signs"]:
                        resp += f"  • {s}\n"
                    resp += "\n**Treatment:**\n"
                    for t in data["treatment"]:
                        resp += f"  ✅ {t}\n"
                    resp += f"\n🛡️ **Prevention:** {data['prevention']}\n"
                    resp += f"⏰ **Urgency:** {data.get('urgency','Moderate')}\n\n"
            return resp, 0.87
        # Try to match from symptoms
        if entities.get("symptoms"):
            return self._handle_symptoms(entities, ctx)
        return ("Which pest are you dealing with? Common ones: Spider Mites, Fungus Gnats, "
                "Thrips, Aphids, Powdery Mildew, Bud Rot, Root Rot. Describe what you see!"), 0.55

    def _handle_stage(self, entities, ctx):
        stages = entities.get("stages", [])
        plant = ctx.get("plant")
        ptype = plant.get("plant_type", "Photoperiod") if plant else "Photoperiod"
        if stages:
            return self.stage_guidance(stages[0], ptype)
        elif plant:
            return self.stage_guidance(plant.get("stage", "Vegetative"), ptype)
        return self.stage_guidance("Vegetative", ptype)

    def _handle_watering(self, ctx):
        resp = "💧 **Watering Guide**\n\n"
        resp += ("**How to tell when to water:**\n"
                 "  • **Lift test** — pick up the pot. Light = water. Heavy = wait.\n"
                 "  • **Finger test** — dry 1-2 inches deep = time to water\n"
                 "  • Slightly droopy leaves = thirsty (but don't wait for this regularly)\n\n"
                 "**Good watering practice:**\n"
                 "  ✅ Water slowly until 10-20% runoff from bottom\n"
                 "  ✅ Water the entire pot evenly, not just the center\n"
                 "  ✅ Water temp: 65-72°F (18-22°C)\n"
                 "  ✅ Let medium dry between waterings (not bone dry in soil)\n"
                 "  ❌ Don't water on a strict schedule — check the plant\n"
                 "  ❌ Don't let plants sit in runoff water\n\n"
                 "**Overwatering signs:** Droopy leaves, dark green, slow growth, fungus gnats\n"
                 "**Underwatering signs:** Wilting, dry/crispy, very lightweight pot, leaves curling\n\n"
                 "💡 *Coco coir* can handle more frequent watering than soil — it's hard to overwater coco.")
        # Add context
        plant = ctx.get("plant")
        if plant:
            events = ctx.get("events", [])
            water_evts = [e for e in events if e.get("event_type") in ("Watering", "Feeding")]
            if water_evts:
                last = water_evts[0].get("event_date", "")[:10]
                resp += f"\n\n📌 Your last watering of **{plant['name']}** was on {last}."
        return resp

    def _handle_nutrients(self, entities, ctx):
        plant = ctx.get("plant")
        stage = plant.get("stage", "Vegetative") if plant else "Vegetative"
        resp = "🧪 **Nutrient Feeding Guide**\n\n"
        resp += ("**N-P-K Basics:** Nitrogen (growth) / Phosphorus (roots, flowers) / Potassium (health, water)\n\n"
                 "**By Stage:**\n"
                 "  🌱 Seedling: Plain water → 1/4 strength (EC 0.4-0.6)\n"
                 "  🌿 Veg: Full strength, high N ratio 3-1-2 (EC 1.0-1.6)\n"
                 "  🌸 Flower: Full strength, high PK ratio 1-3-2 (EC 1.2-2.0). PK booster wk 4-6.\n"
                 "  🍂 Flush: Zero nutrients. Plain pH'd water.\n\n"
                 "**Golden Rules:**\n"
                 "  ✅ Start at 50% recommended dose and increase\n"
                 "  ✅ Always pH AFTER mixing nutrients\n"
                 "  ✅ Less is more — easier to add than fix burn\n"
                 "  ✅ General pattern: feed → feed → water → feed → feed → water\n"
                 "  ❌ Never mix concentrated nutrients together before diluting\n"
                 "  ❌ Don't feed freshly transplanted plants for 1-2 weeks\n")
        if plant:
            resp += f"\n📌 **{plant['name']}** is in **{stage}**"
            if stage in STAGE_GUIDE:
                needs = STAGE_GUIDE[stage].get("nutrient_needs", "")
                if needs:
                    resp += f" — recommended: {needs}"
        return resp

    def _handle_ph_ec(self, entities, ctx):
        plant = ctx.get("plant")
        medium = ""
        if plant:
            medium = plant.get("medium", "")
        resp = "⚗️ **pH & EC Guide**\n\n"
        # Determine medium type
        is_hydro = any(w in medium.lower() for w in ["coco","hydro","dwc","perlite","rock"]) if medium else False
        if is_hydro or any(w in entities.get("symptoms",[]) for w in ["coco","hydro"]):
            info = PH_LOCKOUT["hydro_coco"]
            resp += f"**Coco / Hydro:** Optimal pH {info['optimal'][0]}-{info['optimal'][1]} (sweet spot {info['sweet_spot'][0]}-{info['sweet_spot'][1]})\n\n"
        else:
            info = PH_LOCKOUT["soil"]
            resp += f"**Soil:** Optimal pH {info['optimal'][0]}-{info['optimal'][1]} (sweet spot {info['sweet_spot'][0]}-{info['sweet_spot'][1]})\n\n"

        resp += "**Lockout Zones:**\n"
        for zone, nutrients in info["lockout_zones"].items():
            resp += f"  • {zone.replace('_',' ')}: locks out {', '.join(nutrients)}\n"

        resp += ("\n**Key Rules:**\n"
                 "  ✅ Always pH AFTER adding all nutrients\n"
                 "  ✅ Measure input AND runoff pH\n"
                 "  ✅ Small pH drift in soil is normal\n"
                 "  ✅ In hydro/coco: check and adjust daily\n")

        # Context from data
        if plant:
            events = ctx.get("events", [])
            ph_evts = [e for e in events if e.get("ph") is not None]
            if ph_evts:
                last_ph = ph_evts[0]["ph"]
                resp += f"\n📌 Last recorded pH for **{plant['name']}**: {last_ph}"
        return resp

    def _handle_vpd(self, entities, ctx):
        plant = ctx.get("plant")
        stage = plant.get("stage", "Vegetative") if plant else "Vegetative"
        temp = entities["numbers"].get("temp")
        rh = entities["numbers"].get("rh")

        resp = "📊 **VPD (Vapor Pressure Deficit)**\n\n"
        resp += ("VPD measures the drying power of air. It drives transpiration.\n\n"
                 "**Targets by Stage:**\n"
                 "  🌱 Seedling/Clone: 0.4–0.8 kPa\n"
                 "  🌿 Vegetative: 0.8–1.2 kPa\n"
                 "  🌸 Early Flower: 1.0–1.2 kPa\n"
                 "  🌺 Mid Flower: 1.2–1.4 kPa\n"
                 "  🍂 Late Flower: 1.3–1.5 kPa\n\n")

        if temp and rh:
            vpd = calc_vpd(temp, rh)
            resp += f"**Your conditions:** {temp}°C / {rh}% RH → VPD = **{vpd:.2f} kPa**\n"
            target = STAGE_GUIDE.get(stage, {}).get("vpd_target")
            if target:
                if vpd < target[0]:
                    ideal = ideal_rh_for_vpd(temp, target[0])
                    resp += f"  → Low for {stage}. Try lowering RH to ~{ideal:.0f}% or raising temp.\n"
                elif vpd > target[1]:
                    ideal = ideal_rh_for_vpd(temp, target[1])
                    resp += f"  → High for {stage}. Try raising RH to ~{ideal:.0f}% or lowering temp.\n"
                else:
                    resp += f"  → ✅ In range for {stage}!\n"
        else:
            if stage in STAGE_GUIDE:
                target = STAGE_GUIDE[stage].get("vpd_target")
                if target:
                    resp += f"📌 For **{stage}**: target {target[0]}-{target[1]} kPa\n"
                    resp += f"   At 25°C, that means RH of ~{ideal_rh_for_vpd(25, target[1]):.0f}%-{ideal_rh_for_vpd(25, target[0]):.0f}%\n"

        resp += "\n💡 Leaf temp is typically 2°C below air temp with good airflow."
        return resp

    def _handle_temp_rh(self, entities, ctx):
        plant = ctx.get("plant")
        stage = plant.get("stage", "Vegetative") if plant else "Vegetative"
        if stage in STAGE_GUIDE:
            g = STAGE_GUIDE[stage]
            resp = f"🌡️ **Environment Targets for {stage}**\n\n"
            if g.get("temp_range"):
                resp += f"Temperature: {g['temp_range'][0]}-{g['temp_range'][1]}°C ({int(g['temp_range'][0]*1.8+32)}-{int(g['temp_range'][1]*1.8+32)}°F)\n"
            if g.get("rh_range"):
                resp += f"Humidity: {g['rh_range'][0]}-{g['rh_range'][1]}%\n"
            if g.get("vpd_target"):
                resp += f"VPD: {g['vpd_target'][0]}-{g['vpd_target'][1]} kPa\n"
            resp += f"\n**Tips:**\n"
            resp += "  • Night temp should drop 5-10°F from day (helps terpene development in flower)\n"
            resp += "  • Temps below 60°F slow growth significantly\n"
            resp += "  • Temps above 85°F cause heat stress, taco leaves, foxtailing\n"
            resp += "  • Lower humidity in flower reduces mold/bud rot risk\n"
            return resp
        return "Tell me what stage your plant is in and I'll give you specific environment targets."

    def _handle_lighting(self, entities, ctx):
        plant = ctx.get("plant")
        stage = plant.get("stage", "Vegetative") if plant else "Vegetative"
        ptype = plant.get("plant_type", "Photoperiod") if plant else "Photoperiod"
        is_auto = "auto" in ptype.lower()
        g = STAGE_GUIDE.get(stage, {})
        light = g.get("light_hours_auto") if is_auto else g.get("light_hours_photo", "18/6")
        ppfd = g.get("ppfd", (400, 600))
        resp = f"💡 **Lighting for {stage}** ({'Auto' if is_auto else 'Photo'})\n\n"
        resp += f"Schedule: **{light}**\n"
        resp += f"PPFD: **{ppfd[0]}-{ppfd[1]}** µmol/m²/s\n\n"
        resp += ("**Distance Guide (approximate):**\n"
                 "  • Seedling: 24-30 inches\n  • Veg: 18-24 inches\n  • Flower: 12-18 inches\n"
                 "  (Adjust based on actual PPFD readings and plant response)\n\n"
                 "**Signs of too much light:** Bleaching, taco leaves, foxtailing\n"
                 "**Signs of too little light:** Stretching, loose buds, slow growth\n")
        if stage == "Flowering" and not is_auto:
            resp += "\n⚠️ **12/12 for photoperiod flowering — ZERO light leaks during the dark period!**"
        return resp

    def _handle_training(self, entities, ctx):
        plant = ctx.get("plant")
        is_auto = "auto" in str(plant.get("plant_type","")).lower() if plant else False
        techs = entities.get("training", [])
        if techs:
            tech_name = techs[0]
            if tech_name in TRAINING_TECHNIQUES:
                data = TRAINING_TECHNIQUES[tech_name]
                resp = f"✂️ **{tech_name}**\n"
                resp += f"Difficulty: {data['difficulty']} | When: {data['stage']} | Yield boost: {data.get('yield_boost','N/A')}\n"
                resp += f"Auto-safe: {'✅ Yes' if data['auto_safe'] else '❌ No'} | Recovery: {data['recovery_days']} days\n\n"
                resp += f"{data['description']}\n\n"
                resp += "**Steps:**\n"
                for i, s in enumerate(data['steps'], 1):
                    resp += f"  {i}. {s}\n"
                resp += "\n**Benefits:** " + ", ".join(data['benefits'])
                resp += "\n**Cautions:** " + ", ".join(data['cautions'][:3])
                if is_auto and not data['auto_safe']:
                    resp += f"\n\n⚠️ Your plant is an autoflower — **{tech_name} is NOT recommended for autos** due to limited veg time."
                return resp
        # General training overview
        resp = "✂️ **Training Techniques**\n\n"
        if is_auto:
            resp += "⚠️ Your plant is an autoflower — only auto-safe techniques recommended!\n\n"
        for name, data in TRAINING_TECHNIQUES.items():
            auto_icon = "✅" if data["auto_safe"] else "❌"
            if is_auto and not data["auto_safe"]:
                continue
            resp += f"  **{name}** — {data['difficulty']} | {auto_icon} Auto | +{data.get('yield_boost','?')} yield\n"
            resp += f"    {data['description'][:80]}...\n\n"
        return resp

    def _handle_harvest(self, ctx):
        plant = ctx.get("plant")
        resp = "🌾 **Harvest Timing Guide**\n\n"
        resp += ("**Trichome Method (most accurate — use a jeweler's loupe or USB microscope):**\n"
                 "  🔬 Clear/transparent = too early, still developing\n"
                 "  ☁️ Cloudy/milky = peak THC, more cerebral/energetic high\n"
                 "  🟤 Amber = THC converting to CBN, more sedative/body high\n\n"
                 "**Sweet spot:** 80-90% cloudy + 10-20% amber\n"
                 "  • Want energetic? Harvest at mostly cloudy, minimal amber\n"
                 "  • Want couch-lock? Wait for 30%+ amber\n\n"
                 "**Pistil Method (less reliable):**\n"
                 "  • 50-70% brown pistils = getting close\n"
                 "  • 80-90% brown = likely ready, confirm with trichomes\n\n"
                 "**Pre-harvest checklist:**\n"
                 "  1. Flush 7-14 days with plain water\n"
                 "  2. Optional: 48h dark period (debated — some say boosts resin)\n"
                 "  3. Harvest in morning before lights turn on\n"
                 "  4. Prepare drying space: 60°F, 60% RH, dark, gentle air\n")
        if plant and plant.get("flower_date"):
            try:
                fd = datetime.strptime(str(plant["flower_date"])[:10], "%Y-%m-%d")
                fw = (datetime.now() - fd).days // 7
                resp += f"\n📌 **{plant['name']}** is in flower week **{fw}**."
                strain = plant.get("strain_name", "")
                for s in STRAIN_LIBRARY:
                    if s["name"].lower() in strain.lower():
                        resp += f" {strain} typically finishes weeks {s['flowering_weeks_min']}-{s['flowering_weeks_max']}."
                        break
            except Exception:
                pass
        return resp

    def _handle_yield(self, ctx):
        return ("⚖️ **Yield Estimation**\n\n"
                "Rough rule of thumb:\n"
                "  • **LED:** 1.0-2.0 grams per watt (experienced grower)\n"
                "  • **HPS:** 0.5-1.0 grams per watt\n"
                "  • Beginners: expect 0.5-0.8 g/W\n\n"
                "**Biggest yield factors:**\n"
                "  1. Light intensity and coverage (PPFD across canopy)\n"
                "  2. Training (SCROG/mainlining can boost 40-60%)\n"
                "  3. Genetics (strain choice matters hugely)\n"
                "  4. Environment (VPD, temp, CO2)\n"
                "  5. Nutrition and pH management\n"
                "  6. Experience and attention\n\n"
                "💡 Focus on mastering environment and training — they have the biggest impact.")

    def _handle_checkup(self, ctx):
        plant = ctx.get("plant")
        if not plant:
            return "Select a plant from the dropdown above, and I'll give you a full checkup with alerts and next steps!"

        resp = f"🌿 **Checkup: {plant['name']}**\n\n"
        stage = plant.get("stage", "?")
        ptype = plant.get("plant_type", "?")
        resp += f"**Stage:** {stage} | **Type:** {ptype}\n"
        if plant.get("strain_name"):
            resp += f"**Strain:** {plant['strain_name']}\n"

        # Days tracking
        try:
            ds = (datetime.now() - datetime.strptime(str(plant.get("start_date",""))[:10], "%Y-%m-%d")).days
            resp += f"**Day:** {ds} from start\n"
        except (ValueError, TypeError): pass
        if plant.get("flower_date"):
            try:
                fd = (datetime.now() - datetime.strptime(str(plant["flower_date"])[:10], "%Y-%m-%d")).days
                resp += f"**Flower week:** {fd//7}\n"
            except (ValueError, TypeError): pass

        # Alerts
        alerts = self.proactive_alerts(ctx)
        if alerts:
            resp += "\n**⚠️ Alerts:**\n"
            for a in alerts:
                icon = "⚠️" if a["type"] == "warning" else "ℹ️"
                resp += f"  {icon} {a['message']}\n"

        # Stage targets
        if stage in STAGE_GUIDE:
            g = STAGE_GUIDE[stage]
            resp += f"\n**Current Targets:**\n"
            if g.get("temp_range"): resp += f"  🌡️ Temp: {g['temp_range'][0]}-{g['temp_range'][1]}°C\n"
            if g.get("rh_range"): resp += f"  💧 RH: {g['rh_range'][0]}-{g['rh_range'][1]}%\n"
            if g.get("vpd_target"): resp += f"  📊 VPD: {g['vpd_target'][0]}-{g['vpd_target'][1]} kPa\n"

        # Next action
        resp += f"\n**Next Steps:**\n{self.suggest_next_action(ctx)}"
        return resp

    def _handle_strain(self, entities, message):
        msg = message.lower()
        for s in STRAIN_LIBRARY:
            if s["name"].lower() in msg:
                resp = f"🌿 **{s['name']}** — {s['strain_type']}\n\n"
                resp += f"Genetics: {s['genetics']}\n"
                resp += f"Flowering: {s['flowering_weeks_min']}-{s['flowering_weeks_max']} weeks\n"
                resp += f"THC: {s['thc_range']}\nYield: {s.get('yield_indoor','N/A')}\n"
                resp += f"Difficulty: {s['difficulty']}\n\n{s['description']}\n"
                resp += f"\nTerpenes: {s['terpenes']}"
                return resp
        # List all
        resp = "🌿 **Strain Library**\n\n"
        for s in STRAIN_LIBRARY:
            auto = " 🔄" if s.get("is_autoflower") else ""
            resp += f"  • **{s['name']}**{auto} — {s['strain_type']} | {s['flowering_weeks_min']}-{s['flowering_weeks_max']}wk | {s['difficulty']}\n"
        resp += "\n💡 Ask about any specific strain for full details!"
        return resp

    def _handle_glossary(self, message):
        msg = message.lower()
        for term, definition in GLOSSARY.items():
            if term.lower() in msg:
                return f"📖 **{term}**\n\n{definition}"
        # Fuzzy match
        terms = list(GLOSSARY.keys())
        words = [w for w in msg.split() if len(w) > 3]
        for word in words:
            matches = get_close_matches(word, [t.lower() for t in terms], n=1, cutoff=0.6)
            if matches:
                for term in terms:
                    if term.lower() == matches[0]:
                        return f"📖 **{term}**\n\n{GLOSSARY[term]}"
        # List all
        resp = "📖 **Glossary** — ask about any term!\n\n"
        for term in sorted(GLOSSARY.keys()):
            resp += f"  • {term}\n"
        return resp

    def _handle_fallback(self, message, ctx):
        plant = ctx.get("plant")
        if plant:
            return self._handle_checkup(ctx)
        return ("I'm not sure what you're asking about. Try one of these:\n\n"
                "  • Describe symptoms you're seeing\n  • Ask about a growth stage\n"
                "  • Ask about nutrients, pests, pH, VPD\n  • Ask about training techniques\n"
                "  • Ask about cloning or breeding\n  • Ask about harvest timing\n"
                "  • Ask 'what is [term]' for definitions\n\n"
                "The more detail you give, the better I can help!")

    # ════════════════════════════════════════════════════════════════════
    #  ADAPTIVE LEARNING — feedback recording & weight adjustment
    # ════════════════════════════════════════════════════════════════════

    def record_user_feedback(self, plant_id, ai_suggestion, user_correction_or_rating,
                             issue_type="", outcome_details="", rule_id=""):
        """
        Store feedback and immediately trigger learning + self-coding.

        Parameters:
            plant_id: which plant the advice was about
            ai_suggestion: what the AI said
            user_correction_or_rating: either text correction or int rating (1-5)
            issue_type: category like 'deficiency', 'pest', 'watering'
            outcome_details: what actually happened
            rule_id: which rule produced the suggestion
        """
        is_rating = isinstance(user_correction_or_rating, int)
        rating = user_correction_or_rating if is_rating else 0
        correction = "" if is_rating else str(user_correction_or_rating)
        was_correct = 1 if (is_rating and rating >= 4) else (0 if correction else -1)

        try:
            conn = self._get_conn()
            conn.execute(
                "INSERT INTO ai_feedback (plant_id, ai_suggestion, user_correction, rating, issue_type, outcome_details, rule_id, was_correct) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (plant_id, ai_suggestion[:500], correction[:500], rating, issue_type, outcome_details, rule_id, was_correct))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Feedback save error: {e}")

        # Trigger learning in background
        threading.Thread(target=self._learn_and_code, args=(rule_id, was_correct, correction, issue_type), daemon=True).start()

    def _learn_and_code(self, rule_id, was_correct, correction, issue_type):
        """Combined learning + self-coding triggered by feedback."""
        self.apply_learning_from_feedback()
        if correction and issue_type:
            self.self_code_improvement({
                "rule_id": rule_id, "correction": correction,
                "issue_type": issue_type, "was_correct": was_correct})

    def apply_learning_from_feedback(self):
        """Scan all feedback and adjust rule weights accordingly."""
        try:
            conn = self._get_conn()
            rows = conn.execute(
                "SELECT rule_id, was_correct, COUNT(*) as cnt FROM ai_feedback "
                "WHERE rule_id != '' AND was_correct != -1 GROUP BY rule_id, was_correct"
            ).fetchall()
            conn.close()

            adjustments = {}
            for row in rows:
                rid = row["rule_id"]
                if rid not in adjustments:
                    adjustments[rid] = {"correct": 0, "incorrect": 0}
                if row["was_correct"] == 1:
                    adjustments[rid]["correct"] += row["cnt"]
                else:
                    adjustments[rid]["incorrect"] += row["cnt"]

            for rid, counts in adjustments.items():
                if rid in rule_weights:
                    total = counts["correct"] + counts["incorrect"]
                    if total >= 2:
                        accuracy = counts["correct"] / total
                        # Shift weight toward accuracy: >0.5 means the rule is good
                        new_weight = 0.5 + accuracy  # range 0.5 to 1.5
                        # Smooth: blend 70% new, 30% old
                        rule_weights[rid] = round(rule_weights[rid] * 0.3 + new_weight * 0.7, 3)

            self._save_weights()
        except Exception as e:
            print(f"Learning error: {e}")

    # ════════════════════════════════════════════════════════════════════
    #  SELF-CODING ENGINE — generates new Python rule functions
    # ════════════════════════════════════════════════════════════════════

    def self_code_improvement(self, feedback_data):
        """
        Analyze feedback and generate new Python rule code.

        The AI examines patterns in corrections and creates new specialized
        rule functions. Generated code follows strict templates and is
        validated before being written to learned_rules.py.

        Example: If user repeatedly corrects "Nitrogen deficiency" to
        "Magnesium lockout at low pH", the AI generates a new rule:
            def rule_mg_lockout_low_ph(symptoms, leaf_loc, medium, ph, stage):
                score = 0.0
                if ph is not None and ph < 5.8:
                    if "yellowing" in str(symptoms) and leaf_loc == "older":
                        score = 0.85
                return ("Magnesium lockout (pH too low)", score)
        """
        correction = feedback_data.get("correction", "")
        issue_type = feedback_data.get("issue_type", "")
        rule_id = feedback_data.get("rule_id", "")

        if not correction or not issue_type:
            return

        # Generate a safe rule name
        safe_name = re.sub(r'[^a-z0-9]', '_', correction.lower().strip()[:40])
        safe_name = re.sub(r'_+', '_', safe_name).strip('_')
        if not safe_name:
            return
        rule_func_name = f"rule_learned_{safe_name}"

        # Build conditions based on the feedback pattern
        conditions_lines = []
        diag_name = correction[:60]

        # Analyze what kind of rule to generate based on issue type
        if issue_type in ("deficiency", "symptom_diagnosis"):
            # Generate a symptom-matching rule
            conditions_lines.append(f'    # Generated from user correction: "{correction[:80]}"')
            conditions_lines.append(f'    symptom_str = " ".join(str(s) for s in symptoms).lower()')

            # Extract keywords from the correction to build conditions
            corr_lower = correction.lower()
            if "ph" in corr_lower:
                ph_val = re.search(r'ph\s*(\d+\.?\d*)', corr_lower)
                if ph_val:
                    pv = float(ph_val.group(1))
                    conditions_lines.append(f'    if ph is not None and ph < {pv + 0.3}:')
                    conditions_lines.append(f'        score += 0.4')
                else:
                    conditions_lines.append(f'    if ph is not None and (ph < 5.8 or ph > 7.0):')
                    conditions_lines.append(f'        score += 0.3')

            if "lockout" in corr_lower:
                conditions_lines.append(f'    if "yellowing" in symptom_str or "spots" in symptom_str:')
                conditions_lines.append(f'        score += 0.3')

            for nutrient_kw in ["magnesium","calcium","iron","nitrogen","phosphorus","potassium","zinc"]:
                if nutrient_kw in corr_lower:
                    conditions_lines.append(f'    if "{nutrient_kw[:4]}" in symptom_str or "{nutrient_kw}" in symptom_str.lower():')
                    conditions_lines.append(f'        score += 0.2')
                    break

            if "older" in corr_lower or "lower" in corr_lower:
                conditions_lines.append(f'    if leaf_loc == "older":')
                conditions_lines.append(f'        score += 0.2')
            elif "newer" in corr_lower or "new growth" in corr_lower:
                conditions_lines.append(f'    if leaf_loc == "newer":')
                conditions_lines.append(f'        score += 0.2')

            # Default minimum condition
            if len(conditions_lines) <= 2:
                conditions_lines.append(f'    if len(symptoms) > 0:')
                conditions_lines.append(f'        score += 0.1')

        elif issue_type == "pest_disease":
            conditions_lines.append(f'    # Learned pest/disease pattern from feedback')
            conditions_lines.append(f'    symptom_str = " ".join(str(s) for s in symptoms).lower()')
            conditions_lines.append(f'    if any(kw in symptom_str for kw in {repr(correction.lower().split()[:4])}):')
            conditions_lines.append(f'        score += 0.6')

        else:
            # Generic learned rule
            conditions_lines.append(f'    # Generic learned pattern')
            conditions_lines.append(f'    if len(symptoms) > 0:')
            conditions_lines.append(f'        score += 0.3')

        conditions_str = "\n".join(conditions_lines)

        # Fill template
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        code = RULE_TEMPLATES["symptom_rule"].format(
            name=safe_name, description=correction[:80],
            feedback_ids=str(feedback_data.get("id", "?")),
            timestamp=timestamp, conditions=conditions_str,
            diagnosis=diag_name, confidence=0.8)

        # Validate generated code is safe
        if not validate_generated_code(code):
            print(f"Self-coding: generated code failed validation for rule '{rule_func_name}'")
            return

        # Write to learned_rules.py
        try:
            self._write_learned_rule(rule_func_name, code)
            self._load_learned_rules()
            self.rules_generated += 1
            self.last_improvement = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Save to database too
            conn = self._get_conn()
            conn.execute(
                "INSERT OR REPLACE INTO ai_learned_rules (rule_name, rule_code, confidence, created_at) "
                "VALUES (?, ?, ?, datetime('now'))",
                (rule_func_name, code, 0.8))
            conn.commit()
            conn.close()

            print(f"Self-coding: generated new rule '{rule_func_name}'")
        except Exception as e:
            print(f"Self-coding error: {e}")

    def _write_learned_rule(self, func_name, code):
        """Append a new rule to learned_rules.py (create if needed)."""
        header = '# FILE: growforge/learned_rules.py\n# AUTO-GENERATED by GrowForge AI Self-Coding Engine\n# Do not edit manually — this file is managed by the AI.\n\n'

        if not os.path.exists(LEARNED_RULES_PATH):
            with open(LEARNED_RULES_PATH, 'w') as f:
                f.write(header)

        # Check if rule already exists
        with open(LEARNED_RULES_PATH, 'r') as f:
            existing = f.read()

        if func_name in existing:
            # Replace existing rule
            pattern = rf'def {func_name}\(.*?\n(?=def |\Z)'
            updated = re.sub(pattern, code + '\n', existing, flags=re.DOTALL)
            with open(LEARNED_RULES_PATH, 'w') as f:
                f.write(updated)
        else:
            with open(LEARNED_RULES_PATH, 'a') as f:
                f.write('\n' + code + '\n')

    def _load_learned_rules(self):
        """Hot-reload the learned_rules module."""
        try:
            if os.path.exists(LEARNED_RULES_PATH):
                import importlib.util
                spec = importlib.util.spec_from_file_location("learned_rules", LEARNED_RULES_PATH)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                self.learned_module = module
        except Exception as e:
            print(f"Learned rules load error: {e}")
            self.learned_module = None

    # ════════════════════════════════════════════════════════════════════
    #  AUTO-IMPROVE & PERSONALIZED INSIGHTS
    # ════════════════════════════════════════════════════════════════════

    def auto_improve(self):
        """
        Called periodically (every 10 interactions) or on feedback.
        Runs both weight learning and checks for self-coding opportunities.
        """
        self.apply_learning_from_feedback()
        self._load_learned_rules()
        self.last_improvement = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def get_personalized_insights(self, plant_id):
        """Use learned rules + adjusted weights for plant-specific insights."""
        ctx = self.get_context(plant_id)
        alerts = self.proactive_alerts(ctx)
        next_action = self.suggest_next_action(ctx)

        insights = {"alerts": alerts, "next_action": next_action,
                    "weight_adjustments": {k: v for k, v in rule_weights.items() if v != 1.0},
                    "rules_generated": self.rules_generated}
        return insights

    def refine_knowledge_base(self):
        """Full refresh: reload weights, reload learned rules, apply all learning."""
        self._load_saved_weights()
        self._load_learned_rules()
        self.apply_learning_from_feedback()
        self.last_improvement = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def get_improvement_stats(self):
        """Return stats about the AI's self-improvement progress."""
        adjusted = sum(1 for v in rule_weights.values() if v != 1.0)
        try:
            conn = self._get_conn()
            feedback_count = conn.execute("SELECT COUNT(*) FROM ai_feedback").fetchone()[0]
            learned_count = conn.execute("SELECT COUNT(*) FROM ai_learned_rules").fetchone()[0]
            conn.close()
        except Exception:
            feedback_count = 0
            learned_count = 0
        return {
            "interactions": self.interaction_count,
            "feedback_received": feedback_count,
            "rules_generated": learned_count,
            "weights_adjusted": adjusted,
            "last_improvement": self.last_improvement or "Not yet",
        }
