#pragma once

#include "ui/ScrollPage.h"
#include "data/Models.h"

class PlantsTab : public ScrollPage {
    Q_OBJECT
public:
    explicit PlantsTab(MainWindow *main);
    void refresh() override;

private:
    void addOrEdit(const Row &existing);
    void logEvent(const Row &plant);
    void advanceStage(const Row &plant);
    void remove(const Row &plant);
    void exportReport(const Row &plant);
    QWidget *plantCard(const Row &plant);
};
