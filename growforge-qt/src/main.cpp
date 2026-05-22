#include <QApplication>
#include <QDir>
#include <QLabel>
#include <QTimer>

#include "app/Config.h"
#include "app/Theme.h"
#include "app/Paths.h"
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
    app.setWindowIcon(Icons::icon("growing", 64, QColor(Config::DARK.accent)));

    // Data lives in a per-user writable folder (%LOCALAPPDATA%/GrowForge), or next
    // to the executable in portable mode (see app/Paths.h).
    Paths::ensureDirs();
    const QString dbPath = Paths::dbPath();

    if (!Db::init(dbPath)) {
        QLabel err("Failed to open database:\n" + Db::lastError());
        err.show();
        return app.exec();
    }

    // Load/sync the strain library (reference data). Done in one transaction with
    // INSERT OR IGNORE so seeding ~2,400 strains is fast and re-runs skip existing.
    // Note: a new install otherwise starts EMPTY — no demo plants/events. Sample
    // data is opt-in via Settings → Data → "Load sample data".
    if (Db::count("strains") < KB::strainLibrary().size())
        Db::bulkInsertIgnore("strains", KB::strainsAsRows());

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
