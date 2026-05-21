#pragma once

#include <QMainWindow>
#include <QMap>
#include <QString>

class QStackedWidget;
class QPushButton;
class QButtonGroup;
class QComboBox;
class QLabel;
class QLineEdit;
class QVBoxLayout;
class Page;
class ReminderEngine;

class MainWindow : public QMainWindow {
    Q_OBJECT
public:
    explicit MainWindow(QWidget *parent = nullptr);

    // Navigate to a page by key (creating it lazily).
    void navigate(const QString &key);
    // Rebuild the currently-visible page from the database.
    void refreshCurrent();
    // Force a specific page (if built) to refresh.
    void refreshPage(const QString &key);
    // Refresh topbar room selector + counts after data changes.
    void refreshChrome();

    // The active room/environment filter (-1 = all rooms).
    int currentRoomId() const { return m_roomId; }

    void switchTheme(const QString &theme);

signals:
    void roomChanged(int envId);

private:
    struct NavItem { QString key, label, icon, section; };

    void buildSidebar(QVBoxLayout *sideLayout);
    void buildTopBar();
    Page *createPage(const QString &key);
    void updateNavIcons();

    QStackedWidget *m_stack = nullptr;
    QButtonGroup *m_navGroup = nullptr;
    QMap<QString, QPushButton *> m_navButtons;
    QMap<QString, Page *> m_pages;
    QString m_current;

    QLabel *m_crumb = nullptr;
    QComboBox *m_roomCombo = nullptr;
    QLineEdit *m_search = nullptr;

    QList<NavItem> m_nav;
    int m_roomId = -1;
    ReminderEngine *m_reminders = nullptr;
};
