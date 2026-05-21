#pragma once

#include "ui/ScrollPage.h"

class SettingsTab : public ScrollPage {
    Q_OBJECT
public:
    explicit SettingsTab(MainWindow *main);
    void refresh() override;
};
