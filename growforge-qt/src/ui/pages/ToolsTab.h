#pragma once

#include "ui/Page.h"

class QWidget;

class ToolsTab : public Page {
    Q_OBJECT
public:
    explicit ToolsTab(MainWindow *main);

private:
    QWidget *buildVpd();
    QWidget *buildYield();
    QWidget *buildMixer();
    QWidget *buildTraining();
};
