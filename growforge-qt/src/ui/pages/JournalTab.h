#pragma once

#include "ui/ScrollPage.h"
#include "data/Models.h"

class JournalTab : public ScrollPage {
    Q_OBJECT
public:
    explicit JournalTab(MainWindow *main);
    void refresh() override;

    // Apply a free-text filter (used by the global topbar search).
    void setTextFilter(const QString &text);

private:
    QWidget *eventRow(const Row &e, bool showPlant);
    int m_plantFilter = -1;        // -1 = all plants
    QString m_typeFilter;          // empty = all types
    QString m_textFilter;          // empty = no text filter
};
