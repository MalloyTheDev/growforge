#pragma once

#include "ui/ScrollPage.h"
#include "data/Models.h"

class EnvironmentsTab : public ScrollPage {
    Q_OBJECT
public:
    explicit EnvironmentsTab(MainWindow *main);
    void refresh() override;

private:
    void addOrEdit(const Row &existing);
    void remove(const Row &env);
};
