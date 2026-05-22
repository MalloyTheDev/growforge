#include "data/Database.h"
#include "app/Config.h"

#include <QSqlDatabase>
#include <QSqlQuery>
#include <QSqlError>
#include <QSqlRecord>
#include <QRegularExpression>
#include <QDateTime>
#include <QSet>
#include <QDebug>

namespace Db {

static const char *kConn = "growforge";
static QString g_lastError;

QString lastError() { return g_lastError; }

static QSqlDatabase conn() { return QSqlDatabase::database(kConn); }

// ─── Whitelisting ────────────────────────────────────────────────────────────
static const QSet<QString> kAllowedTables = {
    "settings", "environments", "strains", "plants", "events", "photos",
    "reminders", "clone_batches", "clones", "crosses", "phenotypes",
};

static bool validateTable(const QString &t) {
    if (!kAllowedTables.contains(t)) {
        g_lastError = QString("Invalid table name: %1").arg(t);
        qWarning() << g_lastError;
        return false;
    }
    return true;
}

static bool validateColumns(const QList<QString> &cols) {
    static const QRegularExpression safe("^[a-zA-Z_][a-zA-Z0-9_]*$");
    for (const QString &c : cols) {
        if (!safe.match(c).hasMatch()) {
            g_lastError = QString("Invalid column name: %1").arg(c);
            qWarning() << g_lastError;
            return false;
        }
    }
    return true;
}

// ─── Validation (event bounds, pheno auto-calc) ──────────────────────────────
static void validateEventData(Row &data) {
    static const QMap<QString, QPair<double, double>> bounds = {
        {"ph", {0.0, 14.0}}, {"ec", {0.0, 20.0}}, {"ppm", {0.0, 10000.0}},
        {"temp", {-10.0, 60.0}}, {"humidity", {0.0, 100.0}},
        {"vpd", {0.0, 5.0}}, {"water_ml", {0.0, 100000.0}},
    };
    for (auto it = bounds.constBegin(); it != bounds.constEnd(); ++it) {
        const QString &f = it.key();
        if (data.contains(f) && !data.value(f).isNull()) {
            bool ok = false;
            double v = data.value(f).toDouble(&ok);
            if (!ok || v < it.value().first || v > it.value().second)
                data[f] = QVariant(); // reject out of range
        }
    }
}

static void autoCalcPhenoScore(Row &data) {
    static const QStringList fields = {
        "vigor_score", "structure_score", "yield_score", "terpene_score",
        "resin_score", "pest_resistance_score", "mold_resistance_score",
        "bag_appeal_score", "potency_score", "flavor_score",
    };
    QList<double> scores;
    for (const QString &f : fields) {
        if (data.contains(f) && !data.value(f).isNull()) {
            bool ok = false;
            double v = data.value(f).toDouble(&ok);
            if (ok) scores << v;
        }
    }
    if (!scores.isEmpty()) {
        double sum = 0; for (double x : scores) sum += x;
        data["overall_score"] = QString::number(sum / scores.size(), 'f', 1).toDouble();
    }
}

// ─── Query helpers ───────────────────────────────────────────────────────────
static Rows toRows(QSqlQuery &q) {
    Rows out;
    while (q.next()) {
        Row r;
        const QSqlRecord rec = q.record();
        for (int i = 0; i < rec.count(); ++i)
            r.insert(rec.fieldName(i), q.value(i));
        out << r;
    }
    return out;
}

static bool exec(QSqlQuery &q) {
    if (!q.exec()) {
        g_lastError = q.lastError().text();
        qWarning() << "SQL error:" << g_lastError << "\n  query:" << q.lastQuery();
        return false;
    }
    return true;
}

// ─── Schema ──────────────────────────────────────────────────────────────────
static void createSchema() {
    QSqlQuery q(conn());
    const QStringList ddl = {
        R"(CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY, value TEXT NOT NULL))",

        R"(CREATE TABLE IF NOT EXISTS environments (
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
            updated_at TEXT DEFAULT (datetime('now'))))",

        R"(CREATE TABLE IF NOT EXISTS strains (
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
            created_at TEXT DEFAULT (datetime('now'))))",

        R"(CREATE TABLE IF NOT EXISTS plants (
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
            germ_date TEXT, veg_date TEXT, flower_date TEXT, harvest_date TEXT,
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
            FOREIGN KEY (mother_plant_id) REFERENCES plants(id)))",

        R"(CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plant_id INTEGER, environment_id INTEGER,
            event_type TEXT NOT NULL,
            event_date TEXT DEFAULT (datetime('now')),
            title TEXT DEFAULT '', notes TEXT DEFAULT '',
            ph REAL, ec REAL, ppm REAL, temp REAL, humidity REAL, vpd REAL, water_ml REAL,
            nutrient_mix TEXT DEFAULT '', photo_path TEXT DEFAULT '',
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (plant_id) REFERENCES plants(id),
            FOREIGN KEY (environment_id) REFERENCES environments(id)))",

        R"(CREATE TABLE IF NOT EXISTS photos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plant_id INTEGER, environment_id INTEGER, event_id INTEGER,
            file_path TEXT NOT NULL, caption TEXT DEFAULT '',
            taken_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (plant_id) REFERENCES plants(id),
            FOREIGN KEY (event_id) REFERENCES events(id)))",

        R"(CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plant_id INTEGER, environment_id INTEGER,
            reminder_type TEXT NOT NULL, due_date TEXT NOT NULL,
            message TEXT DEFAULT '',
            is_recurring INTEGER DEFAULT 0, recurrence_days INTEGER DEFAULT 0,
            is_completed INTEGER DEFAULT 0, completed_at TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (plant_id) REFERENCES plants(id)))",

        R"(CREATE TABLE IF NOT EXISTS clone_batches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mother_plant_id INTEGER NOT NULL, batch_name TEXT NOT NULL,
            cut_date TEXT DEFAULT (date('now')),
            rooting_method TEXT DEFAULT '', medium TEXT DEFAULT '',
            num_cuts INTEGER DEFAULT 0, notes TEXT DEFAULT '',
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (mother_plant_id) REFERENCES plants(id)))",

        R"(CREATE TABLE IF NOT EXISTS clones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            batch_id INTEGER NOT NULL, clone_name TEXT NOT NULL,
            stage TEXT DEFAULT 'Cut Taken', root_date TEXT, transplant_date TEXT,
            status TEXT DEFAULT 'Active', promoted_plant_id INTEGER,
            notes TEXT DEFAULT '',
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (batch_id) REFERENCES clone_batches(id),
            FOREIGN KEY (promoted_plant_id) REFERENCES plants(id)))",

        R"(CREATE TABLE IF NOT EXISTS crosses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cross_name TEXT NOT NULL,
            mother_plant_id INTEGER, father_plant_id INTEGER,
            mother_strain TEXT DEFAULT '', father_strain TEXT DEFAULT '',
            pollination_date TEXT, seed_harvest_date TEXT,
            seed_count INTEGER DEFAULT 0, generation TEXT DEFAULT 'F1',
            goals TEXT DEFAULT '', notes TEXT DEFAULT '',
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (mother_plant_id) REFERENCES plants(id),
            FOREIGN KEY (father_plant_id) REFERENCES plants(id)))",

        R"(CREATE TABLE IF NOT EXISTS phenotypes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cross_id INTEGER, plant_id INTEGER, pheno_name TEXT NOT NULL,
            vigor_score INTEGER DEFAULT 5, structure_score INTEGER DEFAULT 5,
            yield_score INTEGER DEFAULT 5, terpene_score INTEGER DEFAULT 5,
            resin_score INTEGER DEFAULT 5, pest_resistance_score INTEGER DEFAULT 5,
            mold_resistance_score INTEGER DEFAULT 5, bag_appeal_score INTEGER DEFAULT 5,
            potency_score INTEGER DEFAULT 5, flavor_score INTEGER DEFAULT 5,
            overall_score REAL DEFAULT 5.0, is_keeper INTEGER DEFAULT 0,
            flowering_days INTEGER DEFAULT 0, stretch_ratio REAL DEFAULT 0,
            notes TEXT DEFAULT '',
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (cross_id) REFERENCES crosses(id),
            FOREIGN KEY (plant_id) REFERENCES plants(id)))",
    };
    for (const QString &sql : ddl) {
        q.prepare(sql);
        exec(q);
    }
    const QStringList idx = {
        "CREATE INDEX IF NOT EXISTS idx_plants_env ON plants(environment_id)",
        "CREATE INDEX IF NOT EXISTS idx_plants_active ON plants(is_active)",
        "CREATE INDEX IF NOT EXISTS idx_plants_stage ON plants(stage)",
        "CREATE INDEX IF NOT EXISTS idx_plants_strain ON plants(strain_id)",
        "CREATE INDEX IF NOT EXISTS idx_events_plant ON events(plant_id)",
        "CREATE INDEX IF NOT EXISTS idx_events_date ON events(event_date)",
        "CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type)",
        "CREATE INDEX IF NOT EXISTS idx_photos_plant ON photos(plant_id)",
        "CREATE INDEX IF NOT EXISTS idx_photos_event ON photos(event_id)",
        "CREATE INDEX IF NOT EXISTS idx_reminders_due ON reminders(is_completed, due_date)",
        "CREATE INDEX IF NOT EXISTS idx_clones_batch ON clones(batch_id)",
        "CREATE INDEX IF NOT EXISTS idx_clone_batches_mother ON clone_batches(mother_plant_id)",
        "CREATE INDEX IF NOT EXISTS idx_phenotypes_cross ON phenotypes(cross_id)",
    };
    for (const QString &sql : idx) { q.prepare(sql); exec(q); }
}

// ─── Settings ────────────────────────────────────────────────────────────────
QVariant getSetting(const QString &key, const QVariant &def) {
    QSqlQuery q(conn());
    q.prepare("SELECT value FROM settings WHERE key=?");
    q.addBindValue(key);
    if (exec(q) && q.next()) return q.value(0);
    return def;
}

void setSetting(const QString &key, const QVariant &value) {
    QSqlQuery q(conn());
    q.prepare("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)");
    q.addBindValue(key);
    q.addBindValue(value.toString());
    exec(q);
}

QString getSettingStr(const QString &key, const QString &def) {
    QVariant v = getSetting(key);
    return v.isValid() ? v.toString() : def;
}
int getSettingInt(const QString &key, int def) {
    QVariant v = getSetting(key);
    if (!v.isValid()) return def;
    bool ok = false; int i = v.toString().toInt(&ok);
    return ok ? i : def;
}
bool getSettingBool(const QString &key, bool def) {
    QVariant v = getSetting(key);
    if (!v.isValid()) return def;
    const QString s = v.toString().toLower();
    return s == "true" || s == "1" || s == "yes";
}

static void initDefaultSettings() {
    for (const auto &ds : Config::DEFAULT_SETTINGS) {
        if (!getSetting(ds.key).isValid())
            setSetting(ds.key, QString(ds.value));
    }
}

// ─── init ────────────────────────────────────────────────────────────────────
bool init(const QString &dbPath) {
    if (QSqlDatabase::contains(kConn))
        QSqlDatabase::removeDatabase(kConn);
    QSqlDatabase db = QSqlDatabase::addDatabase("QSQLITE", kConn);
    db.setDatabaseName(dbPath);
    if (!db.open()) {
        g_lastError = db.lastError().text();
        qWarning() << "Failed to open DB:" << g_lastError;
        return false;
    }
    QSqlQuery pragma(db);
    pragma.exec("PRAGMA journal_mode=WAL");
    pragma.exec("PRAGMA foreign_keys=ON");
    createSchema();
    initDefaultSettings();
    return true;
}

// ─── Generic CRUD ────────────────────────────────────────────────────────────
int insertRow(const QString &table, Row data) {
    if (!validateTable(table) || !validateColumns(data.keys())) return -1;
    if (table == "events") validateEventData(data);
    else if (table == "phenotypes") autoCalcPhenoScore(data);

    const QStringList keys = data.keys();
    QStringList placeholders;
    for (int i = 0; i < keys.size(); ++i) placeholders << "?";
    QSqlQuery q(conn());
    q.prepare(QString("INSERT INTO %1 (%2) VALUES (%3)")
                  .arg(table, keys.join(", "), placeholders.join(", ")));
    for (const QString &k : keys) q.addBindValue(data.value(k));
    if (!exec(q)) return -1;
    return q.lastInsertId().toInt();
}

int bulkInsertIgnore(const QString &table, const Rows &rows) {
    if (!validateTable(table) || rows.isEmpty()) return 0;
    QSqlDatabase db = conn();
    const bool inTxn = db.transaction();   // one transaction → one fsync at commit
    QSqlQuery q(db);
    int inserted = 0;
    for (Row data : rows) {
        if (!validateColumns(data.keys())) continue;
        if (table == "events") validateEventData(data);
        else if (table == "phenotypes") autoCalcPhenoScore(data);
        const QStringList keys = data.keys();
        if (keys.isEmpty()) continue;
        QStringList placeholders;
        for (int i = 0; i < keys.size(); ++i) placeholders << "?";
        q.prepare(QString("INSERT OR IGNORE INTO %1 (%2) VALUES (%3)")
                      .arg(table, keys.join(", "), placeholders.join(", ")));
        for (const QString &k : keys) q.addBindValue(data.value(k));
        if (q.exec() && q.numRowsAffected() > 0) ++inserted;
    }
    if (inTxn && !db.commit()) {
        g_lastError = db.lastError().text();
        db.rollback();
    }
    return inserted;
}

void updateRow(const QString &table, int id, Row data) {
    if (!validateTable(table) || !validateColumns(data.keys())) return;
    if (table == "phenotypes") autoCalcPhenoScore(data);
    const QStringList keys = data.keys();
    QStringList sets;
    for (const QString &k : keys) sets << QString("%1=?").arg(k);
    QSqlQuery q(conn());
    q.prepare(QString("UPDATE %1 SET %2 WHERE id=?").arg(table, sets.join(", ")));
    for (const QString &k : keys) q.addBindValue(data.value(k));
    q.addBindValue(id);
    exec(q);
}

void deleteRow(const QString &table, int id) {
    if (!validateTable(table)) return;
    QSqlQuery q(conn());
    q.prepare(QString("DELETE FROM %1 WHERE id=?").arg(table));
    q.addBindValue(id);
    exec(q);
}

Row getRow(const QString &table, int id) {
    if (!validateTable(table)) return {};
    QSqlQuery q(conn());
    q.prepare(QString("SELECT * FROM %1 WHERE id=?").arg(table));
    q.addBindValue(id);
    if (!exec(q)) return {};
    Rows rows = toRows(q);
    return rows.isEmpty() ? Row{} : rows.first();
}

Rows getAll(const QString &table, const QString &where,
            const QVariantList &params, const QString &order) {
    if (!validateTable(table)) return {};
    QString sql = QString("SELECT * FROM %1").arg(table);
    if (!where.isEmpty()) sql += " WHERE " + where;
    if (!order.isEmpty()) sql += " ORDER BY " + order;
    QSqlQuery q(conn());
    q.prepare(sql);
    for (const QVariant &p : params) q.addBindValue(p);
    if (!exec(q)) return {};
    return toRows(q);
}

int count(const QString &table, const QString &where, const QVariantList &params) {
    if (!validateTable(table)) return 0;
    QString sql = QString("SELECT COUNT(*) FROM %1").arg(table);
    if (!where.isEmpty()) sql += " WHERE " + where;
    QSqlQuery q(conn());
    q.prepare(sql);
    for (const QVariant &p : params) q.addBindValue(p);
    if (exec(q) && q.next()) return q.value(0).toInt();
    return 0;
}

// ─── Domain queries ──────────────────────────────────────────────────────────
Rows getActivePlants() {
    return getAll("plants", "is_active=1", {}, "updated_at DESC");
}
Rows getPlantsByEnvironment(int envId) {
    return getAll("plants", "environment_id=? AND is_active=1", {envId});
}
Rows getPlantEvents(int plantId, int limit) {
    QSqlQuery q(conn());
    q.prepare("SELECT * FROM events WHERE plant_id=? ORDER BY event_date DESC LIMIT ?");
    q.addBindValue(plantId);
    q.addBindValue(limit);
    if (!exec(q)) return {};
    return toRows(q);
}
Rows getRecentEvents(int limit) {
    QSqlQuery q(conn());
    q.prepare("SELECT e.*, p.name as plant_name FROM events e "
              "LEFT JOIN plants p ON e.plant_id = p.id "
              "ORDER BY e.event_date DESC LIMIT ?");
    q.addBindValue(limit);
    if (!exec(q)) return {};
    return toRows(q);
}
Rows getPlantPhotos(int plantId) {
    return getAll("photos", "plant_id=?", {plantId}, "taken_at DESC");
}
Rows getDueReminders() {
    const QString now = QDateTime::currentDateTime().toString("yyyy-MM-dd HH:mm:ss");
    return getAll("reminders", "is_completed=0 AND due_date <= ?", {now}, "due_date ASC");
}
Rows getUpcomingReminders(int days) {
    const QDateTime now = QDateTime::currentDateTime();
    const QString nowStr = now.toString("yyyy-MM-dd HH:mm:ss");
    const QString future = now.addDays(days).toString("yyyy-MM-dd HH:mm:ss");
    return getAll("reminders", "is_completed=0 AND due_date BETWEEN ? AND ?",
                  {nowStr, future}, "due_date ASC");
}
Rows getMotherPlants() {
    return getAll("plants", "is_mother=1 AND is_active=1");
}
Rows getCloneBatches(int motherId) {
    if (motherId >= 0)
        return getAll("clone_batches", "mother_plant_id=?", {motherId});
    return getAll("clone_batches");
}
Rows getClonesInBatch(int batchId) {
    return getAll("clones", "batch_id=?", {batchId});
}
Rows getCrosses() {
    return getAll("crosses", QString(), {}, "created_at DESC");
}
Rows getPhenotypes(int crossId) {
    if (crossId >= 0)
        return getAll("phenotypes", "cross_id=?", {crossId});
    return getAll("phenotypes");
}

Row getStats() {
    Row s;
    auto one = [&](const QString &sql) -> int {
        QSqlQuery q(conn());
        q.prepare(sql);
        if (exec(q) && q.next()) return q.value(0).toInt();
        return 0;
    };
    auto oneD = [&](const QString &sql) -> double {
        QSqlQuery q(conn());
        q.prepare(sql);
        if (exec(q) && q.next()) return q.value(0).toDouble();
        return 0.0;
    };
    s["active_plants"]     = one("SELECT COUNT(*) FROM plants WHERE is_active=1");
    s["total_harvested"]   = one("SELECT COUNT(*) FROM plants WHERE stage='Harvested'");
    s["total_events"]      = one("SELECT COUNT(*) FROM events");
    s["environments"]      = one("SELECT COUNT(*) FROM environments");
    s["mothers"]           = one("SELECT COUNT(*) FROM plants WHERE is_mother=1 AND is_active=1");
    s["active_clones"]     = one("SELECT COUNT(*) FROM clones WHERE status='Active'");
    s["crosses"]           = one("SELECT COUNT(*) FROM crosses");
    s["total_yield"]       = oneD("SELECT COALESCE(SUM(yield_grams), 0) FROM plants WHERE stage='Harvested'");
    s["pending_reminders"] = one("SELECT COUNT(*) FROM reminders WHERE is_completed=0");
    s["strains"]           = one("SELECT COUNT(*) FROM strains");
    return s;
}

Rows searchEvents(const QString &query, int plantId) {
    QString safe = query; safe.replace("%", "\\%").replace("_", "\\_");
    const QString like = "%" + safe + "%";
    QString sql = "SELECT e.*, p.name as plant_name FROM events e "
                  "LEFT JOIN plants p ON e.plant_id = p.id "
                  "WHERE (e.notes LIKE ? ESCAPE '\\' OR e.title LIKE ? ESCAPE '\\' "
                  "OR e.event_type LIKE ? ESCAPE '\\')";
    QVariantList params = {like, like, like};
    if (plantId >= 0) { sql += " AND e.plant_id=?"; params << plantId; }
    sql += " ORDER BY e.event_date DESC LIMIT 100";
    QSqlQuery q(conn());
    q.prepare(sql);
    for (const QVariant &p : params) q.addBindValue(p);
    if (!exec(q)) return {};
    return toRows(q);
}

bool runScript(const QString &sql) {
    // The SQLite driver executes one statement per exec(), so split on ';'.
    // First strip full-line "--" comments (otherwise a comment line glued to a
    // statement chunk would be mis-detected). String literals here contain no ';'.
    QString cleaned;
    const QStringList lines = sql.split('\n');
    for (const QString &line : lines) {
        if (line.trimmed().startsWith("--")) continue;
        cleaned += line;
        cleaned += '\n';
    }
    QSqlQuery q(conn());
    const QStringList statements = cleaned.split(';', Qt::SkipEmptyParts);
    bool ok = true;
    for (QString stmt : statements) {
        stmt = stmt.trimmed();
        if (stmt.isEmpty()) continue;
        if (!q.exec(stmt)) {
            // Non-fatal: sample rows may already exist on a re-run.
            g_lastError = q.lastError().text();
            qWarning() << "sample data stmt failed:" << g_lastError;
            ok = false;
        }
    }
    return ok;
}

} // namespace Db
