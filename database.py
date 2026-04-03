# FILE: growforge/database.py
"""
GrowForge — SQLite database setup, schema creation, and CRUD helper functions.
All data is stored locally in growforge.db.
"""

import sqlite3
import json
from datetime import datetime, timedelta
from config import DB_NAME, DEFAULT_SETTINGS


def get_connection():
    """Get a database connection with row factory."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_database():
    """Create all tables if they don't exist."""
    conn = get_connection()
    c = conn.cursor()

    # ─── Settings ───────────────────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    """)

    # ─── Environments (tents/rooms) ─────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS environments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            env_type TEXT DEFAULT 'Indoor Tent',
            medium TEXT DEFAULT 'Soil (Organic)',
            light_type TEXT DEFAULT 'LED (Full Spectrum)',
            light_wattage INTEGER DEFAULT 0,
            light_schedule TEXT DEFAULT '18/6',
            tent_size TEXT DEFAULT '',
            notes TEXT DEFAULT '',
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        )
    """)

    # ─── Strains Library ────────────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS strains (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            breeder TEXT DEFAULT '',
            strain_type TEXT DEFAULT 'Hybrid',
            genetics TEXT DEFAULT '',
            flowering_weeks_min INTEGER DEFAULT 8,
            flowering_weeks_max INTEGER DEFAULT 10,
            thc_range TEXT DEFAULT '',
            cbd_range TEXT DEFAULT '',
            yield_indoor TEXT DEFAULT '',
            yield_outdoor TEXT DEFAULT '',
            difficulty TEXT DEFAULT 'Moderate',
            description TEXT DEFAULT '',
            terpenes TEXT DEFAULT '',
            effects TEXT DEFAULT '',
            is_autoflower INTEGER DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)

    # ─── Plants ─────────────────────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS plants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            strain_id INTEGER,
            strain_name TEXT DEFAULT '',
            plant_type TEXT DEFAULT 'Photoperiod',
            genetics_type TEXT DEFAULT 'Feminized',
            stage TEXT DEFAULT 'Germination',
            environment_id INTEGER,
            mother_plant_id INTEGER,
            breeder_cross_id INTEGER,
            start_date TEXT DEFAULT (date('now')),
            germ_date TEXT,
            veg_date TEXT,
            flower_date TEXT,
            harvest_date TEXT,
            pot_size TEXT DEFAULT '',
            medium TEXT DEFAULT '',
            notes TEXT DEFAULT '',
            is_mother INTEGER DEFAULT 0,
            is_active INTEGER DEFAULT 1,
            yield_grams REAL DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (environment_id) REFERENCES environments(id),
            FOREIGN KEY (strain_id) REFERENCES strains(id),
            FOREIGN KEY (mother_plant_id) REFERENCES plants(id)
        )
    """)

    # ─── Event Logs (journal entries) ───────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plant_id INTEGER,
            environment_id INTEGER,
            event_type TEXT NOT NULL,
            event_date TEXT DEFAULT (datetime('now')),
            title TEXT DEFAULT '',
            notes TEXT DEFAULT '',
            ph REAL,
            ec REAL,
            ppm REAL,
            temp REAL,
            humidity REAL,
            vpd REAL,
            water_ml REAL,
            nutrient_mix TEXT DEFAULT '',
            photo_path TEXT DEFAULT '',
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (plant_id) REFERENCES plants(id),
            FOREIGN KEY (environment_id) REFERENCES environments(id)
        )
    """)

    # ─── Photos ─────────────────────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS photos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plant_id INTEGER,
            environment_id INTEGER,
            event_id INTEGER,
            file_path TEXT NOT NULL,
            caption TEXT DEFAULT '',
            taken_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (plant_id) REFERENCES plants(id),
            FOREIGN KEY (event_id) REFERENCES events(id)
        )
    """)

    # ─── Reminders ──────────────────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plant_id INTEGER,
            environment_id INTEGER,
            reminder_type TEXT NOT NULL,
            due_date TEXT NOT NULL,
            message TEXT DEFAULT '',
            is_recurring INTEGER DEFAULT 0,
            recurrence_days INTEGER DEFAULT 0,
            is_completed INTEGER DEFAULT 0,
            completed_at TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (plant_id) REFERENCES plants(id)
        )
    """)

    # ─── Clone Batches ──────────────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS clone_batches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mother_plant_id INTEGER NOT NULL,
            batch_name TEXT NOT NULL,
            cut_date TEXT DEFAULT (date('now')),
            rooting_method TEXT DEFAULT '',
            medium TEXT DEFAULT '',
            num_cuts INTEGER DEFAULT 0,
            notes TEXT DEFAULT '',
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (mother_plant_id) REFERENCES plants(id)
        )
    """)

    # ─── Individual Clones ──────────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS clones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            batch_id INTEGER NOT NULL,
            clone_name TEXT NOT NULL,
            stage TEXT DEFAULT 'Cut Taken',
            root_date TEXT,
            transplant_date TEXT,
            status TEXT DEFAULT 'Active',
            promoted_plant_id INTEGER,
            notes TEXT DEFAULT '',
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (batch_id) REFERENCES clone_batches(id),
            FOREIGN KEY (promoted_plant_id) REFERENCES plants(id)
        )
    """)

    # ─── Breeding Crosses ───────────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS crosses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cross_name TEXT NOT NULL,
            mother_plant_id INTEGER,
            father_plant_id INTEGER,
            mother_strain TEXT DEFAULT '',
            father_strain TEXT DEFAULT '',
            pollination_date TEXT,
            seed_harvest_date TEXT,
            seed_count INTEGER DEFAULT 0,
            generation TEXT DEFAULT 'F1',
            goals TEXT DEFAULT '',
            notes TEXT DEFAULT '',
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (mother_plant_id) REFERENCES plants(id),
            FOREIGN KEY (father_plant_id) REFERENCES plants(id)
        )
    """)

    # ─── Phenotype Records ──────────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS phenotypes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cross_id INTEGER,
            plant_id INTEGER,
            pheno_name TEXT NOT NULL,
            vigor_score INTEGER DEFAULT 5,
            structure_score INTEGER DEFAULT 5,
            yield_score INTEGER DEFAULT 5,
            terpene_score INTEGER DEFAULT 5,
            resin_score INTEGER DEFAULT 5,
            pest_resistance_score INTEGER DEFAULT 5,
            mold_resistance_score INTEGER DEFAULT 5,
            bag_appeal_score INTEGER DEFAULT 5,
            potency_score INTEGER DEFAULT 5,
            flavor_score INTEGER DEFAULT 5,
            overall_score REAL DEFAULT 5.0,
            is_keeper INTEGER DEFAULT 0,
            flowering_days INTEGER DEFAULT 0,
            stretch_ratio REAL DEFAULT 0,
            notes TEXT DEFAULT '',
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (cross_id) REFERENCES crosses(id),
            FOREIGN KEY (plant_id) REFERENCES plants(id)
        )
    """)

    # ─── Indices for query performance ──────────────────────────────────
    c.execute("CREATE INDEX IF NOT EXISTS idx_plants_env ON plants(environment_id)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_plants_active ON plants(is_active)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_plants_stage ON plants(stage)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_plants_strain ON plants(strain_id)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_events_plant ON events(plant_id)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_events_date ON events(event_date)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_photos_plant ON photos(plant_id)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_photos_event ON photos(event_id)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_reminders_due ON reminders(is_completed, due_date)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_clones_batch ON clones(batch_id)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_clone_batches_mother ON clone_batches(mother_plant_id)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_phenotypes_cross ON phenotypes(cross_id)")

    conn.commit()
    conn.close()


# ─── Settings CRUD ──────────────────────────────────────────────────────────

def get_setting(key, default=None):
    conn = get_connection()
    try:
        row = conn.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
        if row:
            try:
                return json.loads(row["value"])
            except (json.JSONDecodeError, TypeError):
                return row["value"]
        return default
    finally:
        conn.close()


def set_setting(key, value):
    conn = get_connection()
    try:
        val = json.dumps(value) if not isinstance(value, str) else value
        conn.execute(
            "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
            (key, val),
        )
        conn.commit()
    finally:
        conn.close()


def init_default_settings():
    for key, val in DEFAULT_SETTINGS.items():
        if get_setting(key) is None:
            set_setting(key, val)


# ─── Table/Column Whitelisting (SQL injection protection) ──────────────────

_ALLOWED_TABLES = {
    "settings", "environments", "strains", "plants", "events", "photos",
    "reminders", "clone_batches", "clones", "crosses", "phenotypes",
    "ai_feedback", "ai_learned_rules", "ai_rule_weights",
}

def _validate_table(table):
    """Raise ValueError if table name is not in the allowed set."""
    if table not in _ALLOWED_TABLES:
        raise ValueError(f"Invalid table name: {table!r}")

def _validate_columns(columns):
    """Raise ValueError if any column name contains unsafe characters."""
    import re
    _safe_col = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]*$')
    for col in columns:
        if not _safe_col.match(col):
            raise ValueError(f"Invalid column name: {col!r}")


# ─── Data Validation ────────────────────────────────────────────────────────

_FIELD_BOUNDS = {
    "ph": (0.0, 14.0),
    "ec": (0.0, 20.0),
    "ppm": (0.0, 10000.0),
    "temp": (-10.0, 60.0),
    "humidity": (0.0, 100.0),
    "vpd": (0.0, 5.0),
    "water_ml": (0.0, 100000.0),
}


def _validate_event_data(data):
    """Clamp or reject out-of-range numeric fields for events."""
    for field, (lo, hi) in _FIELD_BOUNDS.items():
        if field in data and data[field] is not None:
            try:
                val = float(data[field])
                if val < lo or val > hi:
                    data[field] = None  # reject out-of-range
            except (ValueError, TypeError):
                data[field] = None


_PHENO_SCORE_FIELDS = [
    "vigor_score", "structure_score", "yield_score", "terpene_score",
    "resin_score", "pest_resistance_score", "mold_resistance_score",
    "bag_appeal_score", "potency_score", "flavor_score",
]


def _auto_calc_pheno_score(data):
    """Auto-calculate overall_score from individual scores if not set."""
    scores = []
    for field in _PHENO_SCORE_FIELDS:
        if field in data and data[field] is not None:
            try:
                scores.append(float(data[field]))
            except (ValueError, TypeError):
                pass
    if scores:
        data["overall_score"] = round(sum(scores) / len(scores), 1)


# ─── Generic CRUD ───────────────────────────────────────────────────────────

def insert_row(table, data: dict) -> int:
    _validate_table(table)
    _validate_columns(data.keys())
    if table == "events":
        _validate_event_data(data)
    elif table == "phenotypes":
        _auto_calc_pheno_score(data)
    conn = get_connection()
    try:
        cols = ", ".join(data.keys())
        placeholders = ", ".join(["?"] * len(data))
        cur = conn.execute(
            f"INSERT INTO {table} ({cols}) VALUES ({placeholders})",
            list(data.values()),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def update_row(table, row_id: int, data: dict):
    _validate_table(table)
    _validate_columns(data.keys())
    if table == "phenotypes":
        _auto_calc_pheno_score(data)
    conn = get_connection()
    try:
        sets = ", ".join([f"{k}=?" for k in data.keys()])
        vals = list(data.values()) + [row_id]
        conn.execute(f"UPDATE {table} SET {sets} WHERE id=?", vals)
        conn.commit()
    finally:
        conn.close()


def delete_row(table, row_id: int):
    _validate_table(table)
    conn = get_connection()
    try:
        conn.execute(f"DELETE FROM {table} WHERE id=?", (row_id,))
        conn.commit()
    finally:
        conn.close()


def get_row(table, row_id: int):
    _validate_table(table)
    conn = get_connection()
    try:
        row = conn.execute(f"SELECT * FROM {table} WHERE id=?", (row_id,)).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def get_all(table, where="", params=None, order="id DESC"):
    _validate_table(table)
    conn = get_connection()
    try:
        sql = f"SELECT * FROM {table}"
        if where:
            sql += f" WHERE {where}"
        sql += f" ORDER BY {order}"
        rows = conn.execute(sql, params or []).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


# ─── Domain-specific queries ────────────────────────────────────────────────

def get_active_plants():
    return get_all("plants", where="is_active=1", order="updated_at DESC")


def get_plants_by_environment(env_id):
    return get_all("plants", where="environment_id=? AND is_active=1", params=[env_id])


def get_plant_events(plant_id, limit=100):
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT * FROM events WHERE plant_id=? ORDER BY event_date DESC LIMIT ?",
            (plant_id, limit),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_recent_events(limit=20):
    conn = get_connection()
    try:
        rows = conn.execute(
            """SELECT e.*, p.name as plant_name FROM events e
               LEFT JOIN plants p ON e.plant_id = p.id
               ORDER BY e.event_date DESC LIMIT ?""",
            (limit,),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_plant_photos(plant_id):
    return get_all("photos", where="plant_id=?", params=[plant_id], order="taken_at DESC")


def get_due_reminders():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return get_all(
        "reminders",
        where="is_completed=0 AND due_date <= ?",
        params=[now],
        order="due_date ASC",
    )


def get_upcoming_reminders(days=7):
    now = datetime.now()
    future = (now + timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")
    now_str = now.strftime("%Y-%m-%d %H:%M:%S")
    return get_all(
        "reminders",
        where="is_completed=0 AND due_date BETWEEN ? AND ?",
        params=[now_str, future],
        order="due_date ASC",
    )


def get_mother_plants():
    return get_all("plants", where="is_mother=1 AND is_active=1")


def get_clone_batches(mother_id=None):
    if mother_id:
        return get_all("clone_batches", where="mother_plant_id=?", params=[mother_id])
    return get_all("clone_batches")


def get_clones_in_batch(batch_id):
    return get_all("clones", where="batch_id=?", params=[batch_id])


def get_crosses():
    return get_all("crosses", order="created_at DESC")


def get_phenotypes(cross_id=None):
    if cross_id:
        return get_all("phenotypes", where="cross_id=?", params=[cross_id])
    return get_all("phenotypes")


def get_stats():
    """Get dashboard statistics."""
    conn = get_connection()
    try:
        stats = {}
        stats["active_plants"] = conn.execute(
            "SELECT COUNT(*) FROM plants WHERE is_active=1"
        ).fetchone()[0]
        stats["total_harvested"] = conn.execute(
            "SELECT COUNT(*) FROM plants WHERE stage='Harvested'"
        ).fetchone()[0]
        stats["total_events"] = conn.execute(
            "SELECT COUNT(*) FROM events"
        ).fetchone()[0]
        stats["environments"] = conn.execute(
            "SELECT COUNT(*) FROM environments"
        ).fetchone()[0]
        stats["mothers"] = conn.execute(
            "SELECT COUNT(*) FROM plants WHERE is_mother=1 AND is_active=1"
        ).fetchone()[0]
        stats["active_clones"] = conn.execute(
            "SELECT COUNT(*) FROM clones WHERE status='Active'"
        ).fetchone()[0]
        stats["crosses"] = conn.execute(
            "SELECT COUNT(*) FROM crosses"
        ).fetchone()[0]
        stats["total_yield"] = conn.execute(
            "SELECT COALESCE(SUM(yield_grams), 0) FROM plants WHERE stage='Harvested'"
        ).fetchone()[0]
        stats["pending_reminders"] = conn.execute(
            "SELECT COUNT(*) FROM reminders WHERE is_completed=0"
        ).fetchone()[0]
        stats["strains"] = conn.execute(
            "SELECT COUNT(*) FROM strains"
        ).fetchone()[0]
        return stats
    finally:
        conn.close()


def search_events(query, plant_id=None):
    # Escape LIKE wildcards in user input
    safe_query = query.replace("%", "\\%").replace("_", "\\_")
    conn = get_connection()
    try:
        sql = """SELECT e.*, p.name as plant_name FROM events e
                 LEFT JOIN plants p ON e.plant_id = p.id
                 WHERE (e.notes LIKE ? ESCAPE '\\' OR e.title LIKE ? ESCAPE '\\' OR e.event_type LIKE ? ESCAPE '\\')"""
        params = [f"%{safe_query}%", f"%{safe_query}%", f"%{safe_query}%"]
        if plant_id:
            sql += " AND e.plant_id=?"
            params.append(plant_id)
        sql += " ORDER BY e.event_date DESC LIMIT 100"
        rows = conn.execute(sql, params).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()
