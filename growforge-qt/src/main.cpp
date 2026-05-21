#include <QApplication>
#include <QDir>
#include <QFile>
#include <QLabel>
#include <QTextStream>
#include <QTimer>

#include "app/Config.h"
#include "app/Theme.h"
#include "data/Database.h"
#include "data/KnowledgeBase.h"
#include "ui/MainWindow.h"
#include "ui/widgets/Icons.h"
#include <QIcon>

int main(int argc, char *argv[])
{
    QApplication app(argc, argv);
    app.setApplicationName(Config::APP_NAME);
    app.setApplicationVersion(Config::APP_VERSION);
    app.setOrganizationName("GrowForge");
    app.setWindowIcon(Icons::icon("growing", 64, QColor(Config::DARK.accent)));

    // Data lives next to the executable (mirrors the Python app layout).
    const QString base = QCoreApplication::applicationDirPath();
    QDir().mkpath(base + "/data");
    QDir().mkpath(base + "/photos");
    QDir().mkpath(base + "/exports");
    QDir().mkpath(base + "/backups");
    const QString dbPath = base + "/growforge.db";

    if (!Db::init(dbPath)) {
        QLabel err("Failed to open database:\n" + Db::lastError());
        err.show();
        return app.exec();
    }

    // Load the strain library (once) — mirrors load_strain_library().
    if (Db::count("strains") < KB::strainLibrary().size()) {
        for (const Row &s : KB::strainsAsRows())
            Db::insertRow("strains", s);
    }

    // First-launch sample data.
    if (Db::getSettingBool("first_launch", true)) {
        QFile f(":/sample_data.sql");
        if (f.open(QIODevice::ReadOnly | QIODevice::Text)) {
            Db::runScript(QTextStream(&f).readAll());
        }
        Db::setSetting("first_launch", "false");
    }

    const QString theme = Db::getSettingStr("theme", "dark");
    Theme::apply(&app, theme);

    MainWindow w;
    w.show();

    // Debug aid: GROWFORGE_SHOT=path renders the window to a PNG then exits.
    // Optional GROWFORGE_NAV=<key> navigates first; GROWFORGE_SIZE=WxH resizes.
    const QByteArray shot = qgetenv("GROWFORGE_SHOT");
    if (!shot.isEmpty()) {
        const QByteArray sz = qgetenv("GROWFORGE_SIZE");
        if (!sz.isEmpty()) {
            const auto parts = QString::fromUtf8(sz).split('x');
            if (parts.size() == 2) w.resize(parts[0].toInt(), parts[1].toInt());
        }
        const QByteArray nav = qgetenv("GROWFORGE_NAV");
        if (!nav.isEmpty()) w.navigate(QString::fromUtf8(nav));
        QTimer::singleShot(700, &w, [&w, shot]() {
            w.grab().save(QString::fromUtf8(shot));
            qApp->quit();
        });
    }
    return app.exec();
}
