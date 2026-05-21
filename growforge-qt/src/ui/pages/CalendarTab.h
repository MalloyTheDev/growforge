#pragma once

#include "ui/ScrollPage.h"
#include <QDate>

class CalendarTab : public ScrollPage {
    Q_OBJECT
public:
    explicit CalendarTab(MainWindow *main);
    void refresh() override;

private:
    QDate m_month;   // first day of the displayed month
};
