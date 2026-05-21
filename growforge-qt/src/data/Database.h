#pragma once

#include "data/Models.h"
#include <QString>
#include <QVariant>
#include <QVariantList>

// SQLite data layer (ports database.py) using Qt SQL.
// All functions operate on a single named connection on the GUI thread.
namespace Db {

// Open (creating if needed) the database at dbPath, enable WAL + FK,
// create the schema and default settings. Returns false on failure.
bool init(const QString &dbPath);
QString lastError();

// ─── Settings ──────────────────────────────────────────────────────────────
QVariant getSetting(const QString &key, const QVariant &def = QVariant());
void     setSetting(const QString &key, const QVariant &value);
QString  getSettingStr(const QString &key, const QString &def = QString());
int      getSettingInt(const QString &key, int def = 0);
bool     getSettingBool(const QString &key, bool def = false);

// ─── Generic CRUD (table/column whitelisted) ─────────────────────────────────
int  insertRow(const QString &table, Row data);
void updateRow(const QString &table, int id, Row data);
void deleteRow(const QString &table, int id);
Row  getRow(const QString &table, int id);
Rows getAll(const QString &table, const QString &where = QString(),
            const QVariantList &params = {}, const QString &order = "id DESC");

// ─── Domain queries ──────────────────────────────────────────────────────────
Rows getActivePlants();
Rows getPlantsByEnvironment(int envId);
Rows getPlantEvents(int plantId, int limit = 100);
Rows getRecentEvents(int limit = 20);
Rows getPlantPhotos(int plantId);
Rows getDueReminders();
Rows getUpcomingReminders(int days = 7);
Rows getMotherPlants();
Rows getCloneBatches(int motherId = -1);
Rows getClonesInBatch(int batchId);
Rows getCrosses();
Rows getPhenotypes(int crossId = -1);
Row  getStats();
Rows searchEvents(const QString &query, int plantId = -1);

// Run a raw SQL script (used to load sample data). Returns false on error.
bool runScript(const QString &sql);

// Count rows in a table (whitelisted).
int count(const QString &table, const QString &where = QString(),
          const QVariantList &params = {});

} // namespace Db
