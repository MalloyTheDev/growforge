#pragma once

#include "ui/Page.h"
#include <QStringList>
#include <QSet>

class QVBoxLayout;
class QComboBox;
class QDoubleSpinBox;
class QPushButton;

class DeficiencyWizardTab : public Page {
    Q_OBJECT
public:
    explicit DeficiencyWizardTab(MainWindow *main);

private:
    void diagnose();
    QVBoxLayout *m_results = nullptr;
    QList<QPushButton *> m_symptomChecks;
    QComboBox *m_leaf = nullptr;
    QComboBox *m_medium = nullptr;
    QDoubleSpinBox *m_ph = nullptr;
};
