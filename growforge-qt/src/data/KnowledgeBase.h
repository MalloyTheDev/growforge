#pragma once

#include "data/Models.h"
#include <QJsonObject>
#include <QJsonArray>
#include <QString>
#include <QStringList>

// Loads the embedded knowledge.json (exported verbatim from knowledge_base.py)
// and exposes typed accessors. Singleton, lazily loaded.
namespace KB {

void ensureLoaded();

QJsonArray  strainLibrary();          // 50 strain objects
QJsonObject stageGuide();             // by stage name
QJsonObject stage(const QString &name);
QJsonArray  symptomPatterns();        // 26 symptom dicts
QJsonObject nutrientIssues();         // 10 nutrients
QJsonObject phLockout();              // soil / hydro_coco
QJsonObject pests();                  // 8 pests
QJsonObject trainingTechniques();     // 8 techniques
QJsonObject cloningGuide();
QJsonObject breedingGuide();
QJsonObject vpdZones();               // 7 zones -> [min,max]
QJsonObject ruleWeights();
QJsonObject glossary();

// Default rule weight for a rule_id (1.0 if absent).
double ruleWeight(const QString &ruleId);

// Strain library converted to rows ready for Db::insertRow("strains", ...).
Rows strainsAsRows();

// Convenience: list of strain names (sorted).
QStringList strainNames();

} // namespace KB
