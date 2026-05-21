#pragma once

#include <QWidget>

class MainWindow;

// Base class for all main screens. Pages get a back-pointer to the MainWindow
// so they can navigate, trigger refreshes, and read the active room filter.
class Page : public QWidget {
    Q_OBJECT
public:
    explicit Page(MainWindow *main, QWidget *parent = nullptr)
        : QWidget(parent), m_main(main) {}

    // Rebuild/reload data. Called when the page is shown or data changes.
    virtual void refresh() {}

protected:
    MainWindow *m_main = nullptr;
};
