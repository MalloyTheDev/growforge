#include "ui/MainWindow.h"
#include "ui/Page.h"
#include "ui/Toast.h"
#include "ui/widgets/Icons.h"
#include "ui/widgets/CommonWidgets.h"
#include "app/Config.h"
#include "app/Theme.h"
#include "data/Database.h"
#include "core/ReminderEngine.h"
#include "ui/pages/DashboardTab.h"
#include "ui/pages/PlantsTab.h"
#include "ui/pages/EnvironmentsTab.h"
#include "ui/pages/JournalTab.h"
#include "ui/pages/CalendarTab.h"
#include "ui/pages/GrowingHubTab.h"
#include "ui/pages/CloningTab.h"
#include "ui/pages/BreedingTab.h"
#include "ui/pages/DeficiencyWizardTab.h"
#include "ui/pages/ToolsTab.h"
#include "ui/pages/SettingsTab.h"

#include <QApplication>
#include <QWidget>
#include <QStackedWidget>
#include <QPushButton>
#include <QButtonGroup>
#include <QComboBox>
#include <QLabel>
#include <QLineEdit>
#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QScrollArea>
#include <QPainter>
#include <QPixmap>
#include <QSignalBlocker>

// ── Temporary placeholder page (replaced as real screens land) ───────────────
namespace {
class PlaceholderPage : public Page {
public:
    PlaceholderPage(MainWindow *m, const QString &title, const QString &sub)
        : Page(m) {
        auto *outer = new QVBoxLayout(this);
        outer->setContentsMargins(22, 22, 22, 22);
        outer->addWidget(makePageHeader(title, sub));
        auto *note = makeMuted("This screen is being ported to Qt6. Coming soon.");
        outer->addWidget(note);
        outer->addStretch();
    }
};
} // namespace

MainWindow::MainWindow(QWidget *parent) : QMainWindow(parent) {
    setWindowTitle(Config::APP_NAME + " — " + Config::APP_TAGLINE);
    resize(1280, 820);
    setMinimumSize(1040, 660);

    m_nav = {
        {"dashboard",    "Dashboard",    "dashboard",  "Operate"},
        {"growing",      "Growing",      "growing",    "Operate"},
        {"plants",       "Plants",       "plants",     "Operate"},
        {"environments", "Environments", "env",        "Operate"},
        {"journal",      "Grow Journal", "journal",    "Operate"},
        {"calendar",     "Calendar",     "calendar",   "Operate"},
        {"cloning",      "Cloning",      "cloning",     "Lab"},
        {"breeding",     "Breeding Lab", "breeding",    "Lab"},
        {"deficiency",   "Deficiency",   "deficiency",  "Lab"},
        {"tools",        "Tools",        "tools",       "Lab"},
        {"settings",     "Settings",     "settings",    "System"},
    };

    auto *central = new QWidget;
    auto *root = new QHBoxLayout(central);
    root->setContentsMargins(0, 0, 0, 0);
    root->setSpacing(0);

    // ── Sidebar ──
    auto *sidebar = new QWidget;
    sidebar->setObjectName("Sidebar");
    sidebar->setFixedWidth(248);
    auto *sideLayout = new QVBoxLayout(sidebar);
    sideLayout->setContentsMargins(0, 0, 0, 0);
    sideLayout->setSpacing(0);
    buildSidebar(sideLayout);
    root->addWidget(sidebar);

    // ── Main area ──
    auto *main = new QWidget;
    auto *mainLayout = new QVBoxLayout(main);
    mainLayout->setContentsMargins(0, 0, 0, 0);
    mainLayout->setSpacing(0);

    auto *topbar = new QWidget;
    topbar->setObjectName("TopBar");
    topbar->setFixedHeight(56);
    {
        auto *tl = new QHBoxLayout(topbar);
        tl->setContentsMargins(18, 8, 18, 8);
        tl->setSpacing(10);

        m_crumb = new QLabel;
        m_crumb->setTextFormat(Qt::RichText);
        tl->addWidget(m_crumb);

        tl->addSpacing(6);

        // Room pill
        auto *pill = new QWidget;
        pill->setObjectName("RoomPill");
        auto *pl = new QHBoxLayout(pill);
        pl->setContentsMargins(10, 2, 6, 2);
        pl->setSpacing(6);
        auto *roomLbl = new QLabel("ROOM");
        roomLbl->setStyleSheet(QString("color:%1; font-family:'%2'; font-size:10px;")
                                   .arg(Theme::current().fg2, Theme::monoFamily()));
        pl->addWidget(roomLbl);
        m_roomCombo = new QComboBox;
        m_roomCombo->setMinimumWidth(120);
        pl->addWidget(m_roomCombo);
        tl->addWidget(pill);

        // Search
        m_search = new QLineEdit;
        m_search->setPlaceholderText("Search plants, events, strains…");
        m_search->setClearButtonEnabled(true);
        m_search->setMaximumWidth(360);
        tl->addWidget(m_search, 1);

        tl->addStretch();

        auto *logBtn = new QPushButton("  Log Event");
        logBtn->setProperty("variant", "primary");
        logBtn->setIcon(Icons::icon("plus", 14, QColor("#07110b")));
        connect(logBtn, &QPushButton::clicked, this, [this]() { navigate("journal"); });
        tl->addWidget(logBtn);

        auto *bell = new QPushButton;
        bell->setIcon(Icons::icon("bell", 15, QColor(Theme::current().fg1)));
        bell->setFixedSize(32, 32);
        connect(bell, &QPushButton::clicked, this, [this]() {
            int n = Db::getUpcomingReminders(7).size();
            Toast::show(this, QString("%1 reminder(s) in the next 7 days").arg(n), Toast::Info);
        });
        tl->addWidget(bell);
    }
    mainLayout->addWidget(topbar);

    m_stack = new QStackedWidget;
    mainLayout->addWidget(m_stack, 1);

    root->addWidget(main, 1);
    setCentralWidget(central);

    refreshChrome();
    connect(m_roomCombo, &QComboBox::currentIndexChanged, this, [this](int) {
        m_roomId = m_roomCombo->currentData().toInt();
        emit roomChanged(m_roomId);
        refreshCurrent();
    });

    navigate("dashboard");

    // Reminder engine — surface due reminders as toasts.
    m_reminders = new ReminderEngine(this);
    connect(m_reminders, &ReminderEngine::remindersDue, this, [this](const Rows &due) {
        for (const Row &r : due)
            Toast::show(this, M::s(r, "message", "Reminder due!"), Toast::Info, 6000);
    });
    m_reminders->start(Db::getSettingInt("reminder_check_interval", 60));
}

void MainWindow::buildSidebar(QVBoxLayout *sideLayout) {
    const Config::Palette &p = Theme::current();

    // Brand
    auto *brand = new QWidget;
    auto *bl = new QHBoxLayout(brand);
    bl->setContentsMargins(18, 18, 18, 14);
    bl->setSpacing(10);
    auto *mark = new QLabel;
    mark->setPixmap(Icons::pixmap("growing", 24, QColor(p.accent)));
    bl->addWidget(mark);
    auto *btext = new QVBoxLayout;
    btext->setSpacing(2);
    auto *bname = new QLabel("GrowForge");
    bname->setObjectName("BrandName");
    auto *bver = new QLabel("v" + Config::APP_VERSION + " · command center");
    bver->setObjectName("BrandVer");
    btext->addWidget(bname);
    btext->addWidget(bver);
    bl->addLayout(btext);
    bl->addStretch();
    sideLayout->addWidget(brand);

    // Nav (scrollable)
    auto *scroll = new QScrollArea;
    scroll->setWidgetResizable(true);
    scroll->setFrameShape(QFrame::NoFrame);
    scroll->setHorizontalScrollBarPolicy(Qt::ScrollBarAlwaysOff);
    auto *navW = new QWidget;
    auto *navL = new QVBoxLayout(navW);
    navL->setContentsMargins(10, 6, 10, 6);
    navL->setSpacing(2);

    m_navGroup = new QButtonGroup(this);
    m_navGroup->setExclusive(true);

    QString lastSection;
    for (const NavItem &item : m_nav) {
        if (item.section != lastSection) {
            lastSection = item.section;
            auto *lbl = new QLabel(item.section.toUpper());
            lbl->setObjectName("NavLabel");
            navL->addWidget(lbl);
        }
        auto *btn = new QPushButton("  " + item.label);
        btn->setObjectName("NavButton");
        btn->setCheckable(true);
        btn->setCursor(Qt::PointingHandCursor);
        btn->setIcon(Icons::icon(item.icon, 16, QColor(p.fg2)));
        connect(btn, &QPushButton::clicked, this, [this, item]() { navigate(item.key); });
        m_navGroup->addButton(btn);
        m_navButtons.insert(item.key, btn);
        navL->addWidget(btn);
    }
    navL->addStretch();
    scroll->setWidget(navW);
    sideLayout->addWidget(scroll, 1);

    // Footer
    auto *foot = new QWidget;
    auto *fl = new QVBoxLayout(foot);
    fl->setContentsMargins(10, 8, 10, 12);
    fl->setSpacing(8);

    auto *sysbar = new QWidget;
    sysbar->setObjectName("SysBar");
    auto *sl = new QHBoxLayout(sysbar);
    sl->setContentsMargins(10, 8, 10, 8);
    sl->setSpacing(8);
    auto *dot = new QLabel;
    QPixmap d(8, 8); d.fill(Qt::transparent);
    { QPainter pr(&d); pr.setRenderHint(QPainter::Antialiasing); pr.setBrush(QColor(p.accent));
      pr.setPen(Qt::NoPen); pr.drawEllipse(0, 0, 8, 8); }
    dot->setPixmap(d);
    sl->addWidget(dot);
    auto *sysLbl = new QLabel("System healthy");
    sysLbl->setObjectName("SysBarLabel");
    sl->addWidget(sysLbl);
    sl->addStretch();
    auto *meta = new QLabel("local");
    meta->setObjectName("SysBarMeta");
    sl->addWidget(meta);
    fl->addWidget(sysbar);

    sideLayout->addWidget(foot);
}

void MainWindow::buildTopBar() {}

void MainWindow::updateNavIcons() {
    const Config::Palette &p = Theme::current();
    for (auto it = m_navButtons.begin(); it != m_navButtons.end(); ++it) {
        const QString iconName = [&]() {
            for (const NavItem &n : m_nav) if (n.key == it.key()) return n.icon;
            return QString("circle");
        }();
        const bool active = (it.key() == m_current);
        it.value()->setIcon(Icons::icon(iconName, 16, QColor(active ? p.accent : p.fg2)));
    }
}

Page *MainWindow::createPage(const QString &key) {
    if (key == "dashboard")    return new DashboardTab(this);
    if (key == "plants")       return new PlantsTab(this);
    if (key == "environments") return new EnvironmentsTab(this);
    if (key == "journal")      return new JournalTab(this);
    if (key == "calendar")     return new CalendarTab(this);
    if (key == "growing")      return new GrowingHubTab(this);
    if (key == "cloning")      return new CloningTab(this);
    if (key == "breeding")     return new BreedingTab(this);
    if (key == "deficiency")   return new DeficiencyWizardTab(this);
    if (key == "tools")        return new ToolsTab(this);
    if (key == "settings")     return new SettingsTab(this);

    for (const NavItem &n : m_nav)
        if (n.key == key)
            return new PlaceholderPage(this, n.label, QString());
    return new PlaceholderPage(this, key, QString());
}

void MainWindow::navigate(const QString &key) {
    if (!m_pages.contains(key)) {
        Page *page = createPage(key);
        m_pages.insert(key, page);
        m_stack->addWidget(page);
    }
    m_current = key;
    Page *page = m_pages.value(key);
    m_stack->setCurrentWidget(page);
    page->refresh();

    if (m_navButtons.contains(key))
        m_navButtons.value(key)->setChecked(true);
    updateNavIcons();

    QString label = key;
    for (const NavItem &n : m_nav) if (n.key == key) label = n.label;
    const Config::Palette &p = Theme::current();
    m_crumb->setText(QString("<span style='color:%1'>GrowForge</span> "
                             "<span style='color:%2'>/</span> "
                             "<span style='color:%3;font-weight:600'>%4</span>")
                         .arg(p.fg3, p.fg4, p.fg0, label));
}

void MainWindow::refreshCurrent() {
    if (m_pages.contains(m_current))
        m_pages.value(m_current)->refresh();
    refreshChrome();
}

void MainWindow::refreshPage(const QString &key) {
    if (m_pages.contains(key))
        m_pages.value(key)->refresh();
}

void MainWindow::refreshChrome() {
    if (!m_roomCombo) return;
    QSignalBlocker block(m_roomCombo);
    const int prev = m_roomId;
    m_roomCombo->clear();
    m_roomCombo->addItem("All rooms", -1);
    for (const Row &env : Db::getAll("environments", QString(), {}, "name ASC"))
        m_roomCombo->addItem(M::s(env, "name"), M::i(env, "id"));
    int idx = m_roomCombo->findData(prev);
    m_roomCombo->setCurrentIndex(idx >= 0 ? idx : 0);
    m_roomId = m_roomCombo->currentData().toInt();
}

void MainWindow::switchTheme(const QString &theme) {
    Db::setSetting("theme", theme);
    Theme::apply(qApp, theme);
    // Rebuild pages so per-widget inline styles pick up the new palette.
    for (Page *page : m_pages) { m_stack->removeWidget(page); page->deleteLater(); }
    m_pages.clear();
    updateNavIcons();
    navigate(m_current.isEmpty() ? "dashboard" : m_current);
}
