#include "ui/pages/CalendarTab.h"
#include "ui/widgets/CommonWidgets.h"
#include "ui/widgets/Icons.h"
#include "app/Theme.h"
#include "data/Database.h"

#include <QPushButton>
#include <QHBoxLayout>
#include <QVBoxLayout>
#include <QGridLayout>
#include <QLabel>
#include <QFrame>
#include <QMap>

CalendarTab::CalendarTab(MainWindow *main) : ScrollPage(main) {
    m_month = QDate(QDate::currentDate().year(), QDate::currentDate().month(), 1);
}

void CalendarTab::refresh() {
    auto *root = resetContent();
    const Config::Palette &pal = Theme::current();

    // Header with navigation
    auto *nav = new QWidget;
    auto *nl = new QHBoxLayout(nav);
    nl->setContentsMargins(0, 0, 0, 0);
    auto *prev = new QPushButton;
    prev->setIcon(Icons::icon("chev", 14, QColor(pal.fg1)));
    prev->setFixedWidth(34);
    // chev points right; rotate-free: use a left arrow via text
    prev->setText("‹"); prev->setIcon(QIcon());
    auto *next = new QPushButton("›");
    next->setFixedWidth(34);
    auto *monthLbl = new QLabel(m_month.toString("MMMM yyyy"));
    monthLbl->setStyleSheet(QString("color:%1; font-size:15px; font-weight:600;").arg(pal.fg0));
    connect(prev, &QPushButton::clicked, this, [this]() { m_month = m_month.addMonths(-1); refresh(); });
    connect(next, &QPushButton::clicked, this, [this]() { m_month = m_month.addMonths(1); refresh(); });
    auto *today = new QPushButton("Today");
    connect(today, &QPushButton::clicked, this, [this]() {
        m_month = QDate(QDate::currentDate().year(), QDate::currentDate().month(), 1); refresh();
    });
    nl->addWidget(prev);
    nl->addWidget(monthLbl);
    nl->addWidget(next);
    nl->addSpacing(8);
    nl->addWidget(today);
    nl->addStretch();

    root->addWidget(makePageHeader("Calendar",
        "Events and reminders across the month.", nav));

    // Gather events + reminders for the month.
    const QString prefix = m_month.toString("yyyy-MM");
    QMap<int, int> eventsByDay, remindersByDay;
    for (const Row &e : Db::getAll("events", "event_date LIKE ?", {prefix + "%"}, "event_date ASC")) {
        QDate d = QDate::fromString(M::s(e, "event_date").left(10), "yyyy-MM-dd");
        if (d.isValid()) eventsByDay[d.day()]++;
    }
    for (const Row &r : Db::getAll("reminders", "due_date LIKE ? AND is_completed=0",
                                   {prefix + "%"}, "due_date ASC")) {
        QDate d = QDate::fromString(M::s(r, "due_date").left(10), "yyyy-MM-dd");
        if (d.isValid()) remindersByDay[d.day()]++;
    }

    auto *cal = new Card();
    auto *grid = new QGridLayout;
    grid->setSpacing(6);

    const QStringList wd = {"Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"};
    for (int c = 0; c < 7; ++c) {
        auto *h = new QLabel(wd[c]);
        h->setAlignment(Qt::AlignCenter);
        h->setStyleSheet(QString("color:%1; font-family:'%2'; font-size:10px;")
                             .arg(pal.fg3, Theme::monoFamily()));
        grid->addWidget(h, 0, c);
    }

    const int daysInMonth = m_month.daysInMonth();
    const int firstCol = (m_month.dayOfWeek() - 1); // Mon=0
    const QDate todayDate = QDate::currentDate();

    int rowN = 1, col = firstCol;
    for (int day = 1; day <= daysInMonth; ++day) {
        const QDate cellDate(m_month.year(), m_month.month(), day);
        auto *cell = new QFrame;
        cell->setMinimumHeight(72);
        const bool isToday = (cellDate == todayDate);
        cell->setStyleSheet(QString(
            "QFrame { background:%1; border:1px solid %2; border-radius:6px; }")
            .arg(isToday ? pal.bg3 : pal.bg2,
                 isToday ? pal.accentLine : pal.lineSoft));
        auto *cv = new QVBoxLayout(cell);
        cv->setContentsMargins(7, 6, 7, 6);
        cv->setSpacing(3);
        auto *dnum = new QLabel(QString::number(day));
        dnum->setStyleSheet(QString("color:%1; font-family:'%2'; font-size:11px; %3")
                                .arg(isToday ? pal.accent : pal.fg1, Theme::monoFamily(),
                                     isToday ? "font-weight:600;" : ""));
        cv->addWidget(dnum);

        if (eventsByDay.value(day) > 0) {
            auto *b = makeBadge(QString("%1 log").arg(eventsByDay.value(day)), Tone::Cool);
            cv->addWidget(b, 0, Qt::AlignLeft);
        }
        if (remindersByDay.value(day) > 0) {
            auto *b = makeBadge(QString("%1 due").arg(remindersByDay.value(day)), Tone::Warn);
            cv->addWidget(b, 0, Qt::AlignLeft);
        }
        cv->addStretch();

        grid->addWidget(cell, rowN, col);
        if (++col >= 7) { col = 0; ++rowN; }
    }
    for (int c = 0; c < 7; ++c) grid->setColumnStretch(c, 1);
    cal->addLayout(grid);
    root->addWidget(cal);
    root->addStretch();
}
