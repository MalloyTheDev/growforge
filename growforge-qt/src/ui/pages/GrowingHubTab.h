#pragma once

#include "ui/ScrollPage.h"
#include <QString>

class QWidget;

class GrowingHubTab : public ScrollPage {
    Q_OBJECT
public:
    explicit GrowingHubTab(MainWindow *main);
    void refresh() override;

private:
    QWidget *buildGroup(const QString &groupKey, const QString &guideStage);
    int m_tab = 0;
};
