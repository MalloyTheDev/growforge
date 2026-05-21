#pragma once

#include "ui/ScrollPage.h"
#include "data/Models.h"

class CloningTab : public ScrollPage {
    Q_OBJECT
public:
    explicit CloningTab(MainWindow *main);
    void refresh() override;

private:
    void newBatch();
    void advanceClone(const Row &clone);
    void promoteClone(const Row &clone, const Row &batch);
    QWidget *cloneRow(const Row &clone, const Row &batch);
};
