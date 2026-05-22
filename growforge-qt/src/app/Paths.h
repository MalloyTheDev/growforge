#pragma once

#include <QString>
#include <QCoreApplication>
#include <QStandardPaths>
#include <QFile>
#include <QDir>

// Where GrowForge keeps its database and user files.
//
// Default: a per-user, always-writable folder (%LOCALAPPDATA%/GrowForge on Windows)
// so the app works correctly when installed to a read-only location like Program Files.
//
// Portable mode: if a file named "portable.txt" sits next to the executable, all data
// is kept alongside the executable instead (used by the portable .zip build).
namespace Paths {

inline QString dataRoot() {
    const QString exeDir = QCoreApplication::applicationDirPath();
    if (QFile::exists(exeDir + "/portable.txt"))
        return exeDir;
    QString d = QStandardPaths::writableLocation(QStandardPaths::AppLocalDataLocation);
    return d.isEmpty() ? exeDir : d;
}

inline QString dbPath()     { return dataRoot() + "/growforge.db"; }
inline QString exportsDir() { return dataRoot() + "/exports"; }
inline QString photosDir()  { return dataRoot() + "/photos"; }
inline QString backupsDir() { return dataRoot() + "/backups"; }

inline void ensureDirs() {
    const QStringList dirs = {dataRoot(), exportsDir(), photosDir(), backupsDir()};
    for (const QString &d : dirs) QDir().mkpath(d);
}

} // namespace Paths
