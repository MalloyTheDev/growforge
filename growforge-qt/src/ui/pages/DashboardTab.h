#pragma once

#include "ui/ScrollPage.h"

class DashboardTab : public ScrollPage {
    Q_OBJECT
public:
    explicit DashboardTab(MainWindow *main);
    void refresh() override;
};
