#include "app/Theme.h"

#include <QApplication>
#include <QFont>
#include <QFontDatabase>

namespace Theme {

static QString g_themeName = "dark";

const Config::Palette &current() { return Config::palette(g_themeName); }
QString currentThemeName() { return g_themeName; }

QString sansFamily() {
    const QStringList prefs = {"Geist", "Segoe UI", "Inter", "Roboto"};
    const QStringList have = QFontDatabase::families();
    for (const QString &f : prefs)
        if (have.contains(f)) return f;
    return QApplication::font().family();
}

QString monoFamily() {
    const QStringList prefs = {"Geist Mono", "Cascadia Mono", "Cascadia Code",
                               "Consolas", "JetBrains Mono", "DejaVu Sans Mono"};
    const QStringList have = QFontDatabase::families();
    for (const QString &f : prefs)
        if (have.contains(f)) return f;
    return "monospace";
}

QString buildStyleSheet(const Config::Palette &p) {
    const QString mono = monoFamily();

    QString s;
    s += QString(R"(
* { outline: none; }
QWidget { background: transparent; color: %fg1; font-size: 13px; }
QMainWindow, QDialog { background: %bg0; }

QToolTip {
    background: %bg2; color: %fg0; border: 1px solid %lineStrong;
    padding: 4px 8px; border-radius: 4px;
}

/* ── Sidebar ─────────────────────────────────────────────── */
#Sidebar {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 %sidebar, stop:1 %sidebarEnd);
    border-right: 1px solid %line;
}
#BrandName { color: %fg0; font-size: 15px; font-weight: 600; }
#BrandVer  { color: %fg3; font-family: "%mono"; font-size: 10px; }
#NavLabel  { color: %fg3; font-family: "%mono"; font-size: 10px;
             letter-spacing: 1px; padding: 8px 12px 4px 12px; }

QPushButton#NavButton {
    text-align: left; padding: 8px 12px; border-radius: 6px;
    border: 1px solid transparent; color: %fg1; font-size: 13px;
    background: transparent;
}
QPushButton#NavButton:hover { background: %bg2; color: %fg0; }
QPushButton#NavButton:checked {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 %accentSoft, stop:0.8 transparent);
    color: %fg0; border: 1px solid %accentLine;
}

#SysBar { background: %bg1; border: 1px solid %line; border-radius: 6px; }
#SysBarLabel { color: %fg1; font-size: 11px; }
#SysBarMeta  { color: %fg3; font-family: "%mono"; font-size: 10px; }

/* ── Topbar ──────────────────────────────────────────────── */
#TopBar { background: %bg0; border-bottom: 1px solid %line; }
#Crumb     { color: %fg2; font-size: 12px; }
#CrumbNow  { color: %fg0; font-size: 12px; font-weight: 600; }
#RoomPill {
    background: %bg2; border: 1px solid %lineStrong; border-radius: 999px;
    color: %fg1; padding: 2px 6px;
}
#RoomPill QComboBox { background: transparent; border: 0; padding: 2px 4px; color: %fg0; }

/* ── Page headings ───────────────────────────────────────── */
#PageTitle { color: %fg0; font-size: 22px; font-weight: 600; }
#PageSub   { color: %fg2; font-size: 12px; }
#SectionTitle { color: %fg2; font-family: "%mono"; font-size: 11px;
                letter-spacing: 1px; font-weight: 600; }

/* ── Cards ───────────────────────────────────────────────── */
#Card {
    background: %bg1; border: 1px solid %line; border-radius: 10px;
}
#CardHead { border-bottom: 1px solid %lineSoft; }
#CardTitle { color: %fg2; font-family: "%mono"; font-size: 11px;
             letter-spacing: 1px; font-weight: 600; }

/* ── Buttons ─────────────────────────────────────────────── */
QPushButton {
    background: %bg2; border: 1px solid %lineStrong; border-radius: 6px;
    color: %fg1; padding: 6px 12px; font-size: 12px;
}
QPushButton:hover { background: %bg3; color: %fg0; border-color: %fg4; }
QPushButton:pressed { background: %bg4; }
QPushButton:disabled { color: %fg4; border-color: %lineSoft; }

QPushButton[variant="primary"] {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 %accent2, stop:1 %accent2);
    color: #07110b; border: 1px solid %accent; font-weight: 600;
}
QPushButton[variant="primary"]:hover { background: %accent; color: #06120a; }
QPushButton[variant="ghost"] {
    background: transparent; border-color: transparent; color: %fg2;
}
QPushButton[variant="ghost"]:hover { background: %bg2; color: %fg0; }
QPushButton[variant="danger"] {
    background: rgba(214,95,74,0.16); border: 1px solid rgba(214,95,74,0.45);
    color: %crit;
}
QPushButton[variant="danger"]:hover { background: rgba(214,95,74,0.26); }

/* ── Inputs ──────────────────────────────────────────────── */
QLineEdit, QTextEdit, QPlainTextEdit, QSpinBox, QDoubleSpinBox, QComboBox, QDateEdit {
    background: %bg2; border: 1px solid %lineStrong; border-radius: 6px;
    color: %fg0; padding: 6px 8px; selection-background-color: %accent2;
    selection-color: #07110b;
}
QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QSpinBox:focus,
QDoubleSpinBox:focus, QComboBox:focus, QDateEdit:focus {
    border: 1px solid %accent;
}
QComboBox::drop-down, QDateEdit::drop-down { border: 0; width: 18px; }
QComboBox QAbstractItemView {
    background: %bg2; border: 1px solid %lineStrong; color: %fg0;
    selection-background-color: %accent2; selection-color: #07110b;
    outline: none;
}
QSpinBox::up-button, QSpinBox::down-button,
QDoubleSpinBox::up-button, QDoubleSpinBox::down-button { width: 14px; border: 0; background: %bg3; }

/* ── Labels / helpers ────────────────────────────────────── */
QLabel { color: %fg1; }
QLabel[role="muted"] { color: %fg2; }
QLabel[role="dim"]   { color: %fg3; }
QLabel[role="title"] { color: %fg0; font-size: 22px; font-weight: 600; }
QLabel[mono="true"]  { font-family: "%mono"; }
QLabel[role="metric"] { color: %fg0; font-family: "%mono"; font-size: 28px; font-weight: 600; }

/* ── Tables ──────────────────────────────────────────────── */
QTableWidget, QTableView, QTreeWidget, QListWidget {
    background: %bg1; border: 1px solid %line; border-radius: 8px;
    gridline-color: %lineSoft; color: %fg1; outline: none;
}
QTableWidget::item, QTreeWidget::item, QListWidget::item { padding: 4px 6px; border: 0; }
QTableWidget::item:selected, QTreeWidget::item:selected, QListWidget::item:selected {
    background: %accentSoft; color: %fg0;
}
QHeaderView::section {
    background: %bg2; color: %fg3; border: 0; border-bottom: 1px solid %line;
    padding: 6px 8px; font-family: "%mono"; font-size: 10px; font-weight: 600;
}
QTableCornerButton::section { background: %bg2; border: 0; }

/* ── Tabs (sub-tab bars) ─────────────────────────────────── */
QTabWidget::pane { border: 0; }
QTabBar::tab {
    background: transparent; color: %fg2; padding: 8px 14px;
    border-bottom: 2px solid transparent; margin-right: 2px;
}
QTabBar::tab:selected { color: %fg0; border-bottom: 2px solid %accent; }
QTabBar::tab:hover { color: %fg0; }

/* ── Scrollbars ──────────────────────────────────────────── */
QScrollBar:vertical { background: transparent; width: 10px; margin: 0; }
QScrollBar::handle:vertical { background: %line; border-radius: 5px; min-height: 24px; }
QScrollBar::handle:vertical:hover { background: %lineStrong; }
QScrollBar:horizontal { background: transparent; height: 10px; margin: 0; }
QScrollBar::handle:horizontal { background: %line; border-radius: 5px; min-width: 24px; }
QScrollBar::handle:horizontal:hover { background: %lineStrong; }
QScrollBar::add-line, QScrollBar::sub-line { width: 0; height: 0; }
QScrollBar::add-page, QScrollBar::sub-page { background: transparent; }

QScrollArea { border: 0; background: transparent; }
#PageScroll, #PageScroll > QWidget > QWidget { background: %bg0; }

/* ── Checkboxes / radios ─────────────────────────────────── */
QCheckBox, QRadioButton { color: %fg1; spacing: 6px; }
QCheckBox::indicator, QRadioButton::indicator { width: 16px; height: 16px; }
QCheckBox::indicator { border: 1px solid %lineStrong; border-radius: 4px; background: %bg2; }
QCheckBox::indicator:checked { background: %accent; border-color: %accent; }
QRadioButton::indicator { border: 1px solid %lineStrong; border-radius: 8px; background: %bg2; }
QRadioButton::indicator:checked { background: %accent; border-color: %accent; }

QProgressBar { background: %bg3; border: 0; border-radius: 4px; height: 6px; text-align: center; color: %fg2; }
QProgressBar::chunk { background: %accent; border-radius: 4px; }

QMenu { background: %bg2; border: 1px solid %lineStrong; color: %fg1; }
QMenu::item:selected { background: %accentSoft; color: %fg0; }
)");

    // Token substitution.
    s.replace("%bg0", p.bg0);
    s.replace("%bg1", p.bg1);
    s.replace("%bg2", p.bg2);
    s.replace("%bg3", p.bg3);
    s.replace("%bg4", p.bg4);
    s.replace("%sidebarEnd", p.sidebarEnd);
    s.replace("%sidebar", p.sidebar);
    s.replace("%lineStrong", p.lineStrong);
    s.replace("%lineSoft", p.lineSoft);
    s.replace("%line", p.line);
    s.replace("%fg0", p.fg0);
    s.replace("%fg1", p.fg1);
    s.replace("%fg2", p.fg2);
    s.replace("%fg3", p.fg3);
    s.replace("%fg4", p.fg4);
    s.replace("%accentSoft", p.accentSoft);
    s.replace("%accentLine", p.accentLine);
    s.replace("%accent2", p.accent2);
    s.replace("%accent", p.accent);
    s.replace("%sensor", p.sensor);
    s.replace("%warn", p.warn);
    s.replace("%crit", p.crit);
    s.replace("%violet", p.violet);
    s.replace("%mono", mono);
    return s;
}

void apply(QApplication *app, const QString &theme) {
    g_themeName = (theme == "light") ? "light" : "dark";
    const Config::Palette &p = Config::palette(theme);
    QFont f(sansFamily(), 10);
    app->setFont(f);
    app->setStyleSheet(buildStyleSheet(p));
}

} // namespace Theme
