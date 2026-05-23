#include "ui/pages/DashboardTab.h"
#include "ui/MainWindow.h"
#include "ui/widgets/CommonWidgets.h"
#include "app/Theme.h"
#include "app/Config.h"
#include "data/Database.h"
#include "core/ReminderEngine.h"

#include <QGridLayout>
#include <QHBoxLayout>
#include <QVBoxLayout>
#include <QLabel>
#include <QPushButton>
#include <QDateTime>

static QWidget *plantRow(const Row &p) {
    auto *w = new QWidget;
    auto *row = new QHBoxLayout(w);
    row->setContentsMargins(0, 6, 0, 6);
    row->setSpacing(10);

    auto *col = new QVBoxLayout;
    col->setSpacing(2);
    auto *name = new QLabel(M::s(p, "name"));
    name->setTextFormat(Qt::PlainText);
    name->setStyleSheet(QString("color:%1; font-weight:600;").arg(Theme::current().fg0));
    auto *strain = new QLabel(M::s(p, "strain_name", "—"));
    strain->setProperty("role", "muted");
    strain->setTextFormat(Qt::PlainText);
    strain->setStyleSheet(QString("color:%1; font-size:11px;").arg(Theme::current().fg2));
    col->addWidget(name);
    col->addWidget(strain);
    row->addLayout(col);
    row->addStretch();

    const int day = M::daysSince(M::s(p, "start_date"));
    auto *dayLbl = new QLabel(QString("Day %1").arg(day));
    dayLbl->setProperty("mono", "true");
    dayLbl->setStyleSheet(QString("color:%1; font-family:'%2'; font-size:11px;")
                              .arg(Theme::current().fg2, Theme::monoFamily()));
    row->addWidget(dayLbl);
    row->addWidget(makeStageBadge(M::s(p, "stage")));
    return w;
}

DashboardTab::DashboardTab(MainWindow *main) : ScrollPage(main) {}

void DashboardTab::refresh() {
    auto *root = resetContent();
    root->addWidget(makePageHeader("Dashboard",
        "Overview of your grow — plants, environments, and what needs attention."));

    const Row st = Db::getStats();

    // ── Stat cards grid ──
    auto *grid = new QGridLayout;
    grid->setSpacing(12);
    struct Stat { QString label, key, unit; Tone::T tone; };
    const QList<Stat> stats = {
        {"Active Plants",  "active_plants",     "", Tone::Accent},
        {"Environments",   "environments",      "", Tone::Cool},
        {"Harvested",      "total_harvested",   "", Tone::Ok},
        {"Total Yield",    "total_yield",      "g", Tone::Warn},
        {"Mothers",        "mothers",           "", Tone::Violet},
        {"Crosses",        "crosses",           "", Tone::Violet},
        {"Journal Entries","total_events",      "", Tone::Cool},
        {"Reminders",      "pending_reminders", "", Tone::Warn},
    };
    int col = 0, rowN = 0;
    const int cols = 4;
    for (const Stat &s : stats) {
        QString val = (s.key == "total_yield")
            ? QString::number(M::d(st, s.key), 'f', 0)
            : QString::number(M::i(st, s.key));
        grid->addWidget(new MetricCard(s.label, val, s.unit, s.tone), rowN, col);
        if (++col >= cols) { col = 0; ++rowN; }
    }
    root->addLayout(grid);

    // ── Two columns: active plants | reminders + activity ──
    auto *cols2 = new QHBoxLayout;
    cols2->setSpacing(14);

    // Active plants
    auto *plantsCard = new Card("Active Plants");
    const Rows plants = Db::getActivePlants();
    if (plants.isEmpty()) {
        plantsCard->addWidget(makeMuted("No active plants yet. Add one from the Plants screen."));
    } else {
        int shown = 0;
        for (const Row &p : plants) {
            if (shown) plantsCard->addWidget(hLine());
            plantsCard->addWidget(plantRow(p));
            if (++shown >= 8) break;
        }
    }
    plantsCard->body()->addStretch();
    cols2->addWidget(plantsCard, 3, Qt::AlignTop);

    // Right column
    auto *right = new QVBoxLayout;
    right->setSpacing(14);

    auto *remCard = new Card("Reminders");
    // Incomplete reminders due within the next 7 days, including overdue ones.
    const QString cutoff = QDateTime::currentDateTime().addDays(7).toString("yyyy-MM-dd HH:mm:ss");
    const QString nowStr = QDateTime::currentDateTime().toString("yyyy-MM-dd HH:mm:ss");
    const Rows rem = Db::getAll("reminders", "is_completed=0 AND due_date <= ?", {cutoff}, "due_date ASC");
    if (rem.isEmpty()) {
        remCard->addWidget(makeMuted("Nothing due in the next 7 days."));
    } else {
        int shown = 0;
        for (const Row &r : rem) {
            if (shown++ >= 10) break;
            const int rid = M::i(r, "id");
            const bool overdue = M::s(r, "due_date") <= nowStr;
            auto *line = new QWidget;
            auto *l = new QHBoxLayout(line);
            l->setContentsMargins(0, 4, 0, 4);
            l->setSpacing(8);
            auto *msg = new QLabel(M::s(r, "message"));
            msg->setWordWrap(true);
            msg->setTextFormat(Qt::PlainText);
            l->addWidget(msg, 1);
            l->addWidget(makeBadge(overdue ? "due" : M::s(r, "due_date").left(10),
                                   overdue ? Tone::Crit : Tone::Warn));
            auto *done = new QPushButton("Done");
            done->setFixedHeight(24);
            connect(done, &QPushButton::clicked, this, [this, rid]() {
                ReminderEngine::completeReminder(rid, true);
                if (m_main) m_main->refreshCurrent();
            });
            l->addWidget(done);
            remCard->addWidget(line);
        }
    }
    remCard->body()->addStretch();
    right->addWidget(remCard);

    auto *actCard = new Card("Recent Activity");
    const Rows recent = Db::getRecentEvents(8);
    if (recent.isEmpty()) {
        actCard->addWidget(makeMuted("No activity logged yet."));
    } else {
        for (const Row &e : recent) {
            auto *line = new QWidget;
            auto *l = new QVBoxLayout(line);
            l->setContentsMargins(0, 4, 0, 4);
            l->setSpacing(1);
            auto *top = new QLabel(QString("%1 · %2")
                .arg(M::s(e, "event_type"), M::s(e, "plant_name", "—")));
            top->setStyleSheet(QString("color:%1; font-size:12px;").arg(Theme::current().fg1));
            auto *date = new QLabel(M::s(e, "event_date").left(10));
            date->setStyleSheet(QString("color:%1; font-family:'%2'; font-size:10.5px;")
                                    .arg(Theme::current().fg3, Theme::monoFamily()));
            l->addWidget(top);
            l->addWidget(date);
            actCard->addWidget(line);
        }
    }
    right->addWidget(actCard);
    right->addStretch();

    cols2->addLayout(right, 2);
    root->addLayout(cols2);
    root->addStretch();
}
