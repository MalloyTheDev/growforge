#pragma once

#include "data/Models.h"
#include <QString>

// Report exporters — ports utils/exporters.py (PDF grow report + CSV).
namespace Exporter {

// Render a formatted grow report PDF for one plant. Returns the output path
// (empty on failure). If outPath is empty, a timestamped file is written to
// the given exportDir.
QString exportPlantReportPdf(const Row &plant, const Rows &events,
                             const Row &environment, const QString &exportDir,
                             const QString &outPath = QString());

// Export events to CSV. Returns true on success.
bool exportEventsCsv(const Rows &events, const QString &outPath);

} // namespace Exporter
