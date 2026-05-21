#pragma once

#include "ui/ScrollPage.h"
#include "data/Models.h"

class JournalTab : public ScrollPage {
    Q_OBJECT
public:
    explicit JournalTab(MainWindow *main);
    void refresh() override;

private:
    QWidget *eventRow(const Row &e, bool showPlant);
    int m_plantFilter = -1;        // -1 = all plants
    QString m_typeFilter;          // empty = all types
};
