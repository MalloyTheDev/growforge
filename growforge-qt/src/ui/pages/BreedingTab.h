#pragma once

#include "ui/ScrollPage.h"
#include "data/Models.h"

class BreedingTab : public ScrollPage {
    Q_OBJECT
public:
    explicit BreedingTab(MainWindow *main);
    void refresh() override;

private:
    void newCross();
    void addPhenotype(int crossId);
};
