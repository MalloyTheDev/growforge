#pragma once

#include <QVariantMap>
#include <QVariantList>
#include <QString>
#include <QRegularExpression>
#include <QDate>

// A database row, mirroring the Python dict-based representation.
using Row = QVariantMap;
using Rows = QList<QVariantMap>;

// ─── Safe accessors / parsing (ports helpers.py safe_int / safe_float) ──────
namespace M {

inline int asInt(const QVariant &v, int def = 0) {
    if (!v.isValid() || v.isNull()) return def;
    bool ok = false;
    // Tolerate "12.0" style strings like the Python safe_int (int(float(x))).
    double d = v.toString().toDouble(&ok);
    if (ok) return static_cast<int>(d);
    int i = v.toInt(&ok);
    return ok ? i : def;
}

inline double asDouble(const QVariant &v, double def = 0.0) {
    if (!v.isValid() || v.isNull()) return def;
    bool ok = false;
    double d = v.toString().toDouble(&ok);
    return ok ? d : def;
}

inline QString asStr(const QVariant &v, const QString &def = QString()) {
    if (!v.isValid() || v.isNull()) return def;
    return v.toString();
}

inline bool asBool(const QVariant &v, bool def = false) {
    if (!v.isValid() || v.isNull()) return def;
    const QString s = v.toString().toLower();
    if (s == "1" || s == "true" || s == "yes") return true;
    if (s == "0" || s == "false" || s == "no") return false;
    return v.toBool();
}

inline QString s(const Row &r, const QString &k, const QString &def = QString()) {
    return asStr(r.value(k), def);
}
inline int i(const Row &r, const QString &k, int def = 0) {
    return asInt(r.value(k), def);
}
inline double d(const Row &r, const QString &k, double def = 0.0) {
    return asDouble(r.value(k), def);
}
inline bool b(const Row &r, const QString &k, bool def = false) {
    return asBool(r.value(k), def);
}

// Whole days from a YYYY-MM-DD[...] date string to today (0 if unparseable).
inline int daysSince(const QString &date) {
    const QDate d = QDate::fromString(date.left(10), "yyyy-MM-dd");
    return d.isValid() ? d.daysTo(QDate::currentDate()) : 0;
}

// Extract a numeric id from a "Name (#12)" or "Name [id=12]" style option string.
inline int extractId(const QString &option, int def = -1) {
    static const QRegularExpression re("#(\\d+)");
    auto m = re.match(option);
    if (m.hasMatch()) return m.captured(1).toInt();
    return def;
}

} // namespace M
