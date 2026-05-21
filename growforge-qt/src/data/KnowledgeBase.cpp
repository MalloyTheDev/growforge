#include "data/KnowledgeBase.h"

#include <QFile>
#include <QJsonDocument>
#include <QJsonValue>
#include <QDebug>

namespace KB {

static QJsonObject g_root;
static bool g_loaded = false;

void ensureLoaded() {
    if (g_loaded) return;
    g_loaded = true;
    QFile f(":/knowledge.json");
    if (!f.open(QIODevice::ReadOnly)) {
        qWarning() << "KB: could not open knowledge.json resource";
        return;
    }
    QJsonParseError err{};
    const QJsonDocument doc = QJsonDocument::fromJson(f.readAll(), &err);
    if (err.error != QJsonParseError::NoError) {
        qWarning() << "KB: JSON parse error:" << err.errorString();
        return;
    }
    g_root = doc.object();
}

QJsonArray  strainLibrary()       { ensureLoaded(); return g_root.value("STRAIN_LIBRARY").toArray(); }
QJsonObject stageGuide()          { ensureLoaded(); return g_root.value("STAGE_GUIDE").toObject(); }
QJsonObject stage(const QString &n){ return stageGuide().value(n).toObject(); }
QJsonArray  symptomPatterns()     { ensureLoaded(); return g_root.value("SYMPTOM_PATTERNS").toArray(); }
QJsonObject nutrientIssues()      { ensureLoaded(); return g_root.value("NUTRIENT_ISSUES").toObject(); }
QJsonObject phLockout()           { ensureLoaded(); return g_root.value("PH_LOCKOUT").toObject(); }
QJsonObject pests()               { ensureLoaded(); return g_root.value("PESTS").toObject(); }
QJsonObject trainingTechniques()  { ensureLoaded(); return g_root.value("TRAINING_TECHNIQUES").toObject(); }
QJsonObject cloningGuide()        { ensureLoaded(); return g_root.value("CLONING_GUIDE").toObject(); }
QJsonObject breedingGuide()       { ensureLoaded(); return g_root.value("BREEDING_GUIDE").toObject(); }
QJsonObject vpdZones()            { ensureLoaded(); return g_root.value("VPD_ZONES").toObject(); }
QJsonObject ruleWeights()         { ensureLoaded(); return g_root.value("rule_weights").toObject(); }
QJsonObject glossary()            { ensureLoaded(); return g_root.value("GLOSSARY").toObject(); }

double ruleWeight(const QString &ruleId) {
    const QJsonObject w = ruleWeights();
    return w.contains(ruleId) ? w.value(ruleId).toDouble(1.0) : 1.0;
}

Rows strainsAsRows() {
    Rows rows;
    const QJsonArray arr = strainLibrary();
    // Columns accepted by the strains table.
    static const QStringList cols = {
        "name", "breeder", "strain_type", "genetics",
        "flowering_weeks_min", "flowering_weeks_max", "thc_range", "cbd_range",
        "yield_indoor", "yield_outdoor", "difficulty", "description",
        "terpenes", "effects", "is_autoflower",
    };
    for (const QJsonValue &v : arr) {
        const QJsonObject o = v.toObject();
        Row r;
        for (const QString &c : cols) {
            if (!o.contains(c)) continue;
            const QJsonValue jv = o.value(c);
            if (jv.isArray()) {
                // join list values into a comma string for TEXT columns
                QStringList parts;
                for (const QJsonValue &e : jv.toArray()) parts << e.toString();
                r[c] = parts.join(", ");
            } else if (jv.isDouble()) {
                r[c] = jv.toDouble();
            } else if (jv.isBool()) {
                r[c] = jv.toBool() ? 1 : 0;
            } else {
                r[c] = jv.toString();
            }
        }
        if (!r.isEmpty()) rows << r;
    }
    return rows;
}

QStringList strainNames() {
    QStringList names;
    for (const QJsonValue &v : strainLibrary())
        names << v.toObject().value("name").toString();
    names.sort(Qt::CaseInsensitive);
    return names;
}

} // namespace KB
