#include "core/Exporter.h"
#include "app/Config.h"

#include <QtGlobal>
#include <QTextDocument>
#include <QPrinter>
#include <QPageSize>
#include <QFile>
#include <QTextStream>
#include <QDateTime>
#include <QDir>
#include <QRegularExpression>

namespace Exporter {

static QString esc(const QString &s) { return s.toHtmlEscaped(); }

static QString metricsLine(const Row &e) {
    QStringList parts;
    auto add = [&](const QString &label, const QString &key, const QString &unit) {
        const QVariant v = e.value(key);
        if (v.isValid() && !v.isNull() && !v.toString().isEmpty())
            parts << QString("%1 %2%3").arg(label, v.toString(), unit);
    };
    add("pH", "ph", "");
    add("EC", "ec", "");
    add("Temp", "temp", "&deg;C");
    add("RH", "humidity", "%");
    add("VPD", "vpd", " kPa");
    add("Water", "water_ml", " ml");
    return parts.join(" &nbsp;·&nbsp; ");
}

QString exportPlantReportPdf(const Row &plant, const Rows &events,
                             const Row &environment, const QString &exportDir,
                             const QString &outPath) {
    QString path = outPath;
    if (path.isEmpty()) {
        QString safe = M::s(plant, "name", "plant");
        safe.replace(QRegularExpression("[^A-Za-z0-9_-]+"), "_");
        const QString ts = QDateTime::currentDateTime().toString("yyyyMMddHHmmss");
        QDir().mkpath(exportDir);
        path = exportDir + "/grow_report_" + safe + "_" + ts + ".pdf";
    }

    const QString accent = "#2e7d32";
    QString html;
    html += QString("<html><head><style>"
                    "body{font-family:Helvetica,Arial,sans-serif;color:#282828;}"
                    "h1{color:%1;font-size:20pt;margin:0;}"
                    "h2{color:%1;font-size:13pt;border-bottom:1px solid %1;padding-bottom:3px;margin-top:18px;}"
                    "table{width:100%;border-collapse:collapse;font-size:9pt;margin-top:6px;}"
                    "td,th{border:1px solid #ccc;padding:4px 6px;text-align:left;vertical-align:top;}"
                    "th{background:#eef3ee;}"
                    ".kv td:first-child{font-weight:bold;width:30%;background:#f6f9f6;}"
                    ".meta{color:#888;font-size:8pt;}"
                    "</style></head><body>").arg(accent);

    html += "<h1>GrowForge Grow Report</h1>";
    html += QString("<div class='meta'>Generated %1</div>")
                .arg(QDateTime::currentDateTime().toString("yyyy-MM-dd HH:mm"));

    // Plant info
    html += "<h2>Plant</h2><table class='kv'>";
    auto kv = [&](const QString &k, const QString &v) {
        html += QString("<tr><td>%1</td><td>%2</td></tr>").arg(esc(k), esc(v));
    };
    kv("Name", M::s(plant, "name"));
    kv("Strain", M::s(plant, "strain_name"));
    kv("Type", M::s(plant, "plant_type"));
    kv("Genetics", M::s(plant, "genetics_type"));
    kv("Stage", M::s(plant, "stage"));
    kv("Start date", M::s(plant, "start_date"));
    kv("Medium", M::s(plant, "medium"));
    kv("Pot size", M::s(plant, "pot_size"));
    if (M::d(plant, "yield_grams") > 0)
        kv("Yield", QString::number(M::d(plant, "yield_grams")) + " g");
    if (!M::s(plant, "notes").isEmpty()) kv("Notes", M::s(plant, "notes"));
    html += "</table>";

    // Environment
    if (!environment.isEmpty()) {
        html += "<h2>Environment</h2><table class='kv'>";
        kv("Name", M::s(environment, "name"));
        kv("Type", M::s(environment, "env_type"));
        kv("Light", QString("%1 (%2W)").arg(M::s(environment, "light_type"))
                        .arg(M::i(environment, "light_wattage")));
        kv("Schedule", M::s(environment, "light_schedule"));
        kv("Tent size", M::s(environment, "tent_size"));
        html += "</table>";
    }

    // Journal
    html += "<h2>Grow Journal</h2>";
    if (events.isEmpty()) {
        html += "<p class='meta'>No journal entries.</p>";
    } else {
        html += "<table><tr><th>Date</th><th>Type</th><th>Notes</th><th>Readings</th></tr>";
        for (const Row &e : events) {
            html += QString("<tr><td>%1</td><td>%2</td><td>%3</td><td>%4</td></tr>")
                        .arg(esc(M::s(e, "event_date").left(10)),
                             esc(M::s(e, "event_type")),
                             esc(M::s(e, "notes")),
                             metricsLine(e));
        }
        html += "</table>";
    }
    html += "</body></html>";

    QTextDocument doc;
    doc.setHtml(html);

    QPrinter printer(QPrinter::HighResolution);
    printer.setOutputFormat(QPrinter::PdfFormat);
    printer.setOutputFileName(path);
    printer.setPageSize(QPageSize(QPageSize::A4));
    doc.print(&printer);

    return QFile::exists(path) ? path : QString();
}

bool exportEventsCsv(const Rows &events, const QString &outPath) {
    QFile f(outPath);
    if (!f.open(QIODevice::WriteOnly | QIODevice::Text)) return false;
    QTextStream out(&f);

    QStringList headers;
    if (!events.isEmpty()) headers = events.first().keys();
    out << headers.join(",") << "\n";
    for (const Row &e : events) {
        QStringList cells;
        for (const QString &h : headers) {
            QString v = e.value(h).toString();
            if (v.contains(',') || v.contains('"') || v.contains('\n')) {
                v.replace("\"", "\"\"");
                v = "\"" + v + "\"";
            }
            cells << v;
        }
        out << cells.join(",") << "\n";
    }
    return true;
}

} // namespace Exporter
