#pragma once

#include "ui/Page.h"
#include <QStringList>
#include <QList>

class QVBoxLayout;
class QComboBox;
class QDoubleSpinBox;
class QCheckBox;

class DeficiencyWizardTab : public Page {
    Q_OBJECT
public:
    explicit DeficiencyWizardTab(MainWindow *main);

private:
    void diagnose();
    void clearResults();

    QVBoxLayout *m_results = nullptr;
    QList<QCheckBox *> m_symptomChecks;   // aligned with the curated symptom list
    QComboBox *m_leaf = nullptr;
    QComboBox *m_medium = nullptr;
    QDoubleSpinBox *m_ph = nullptr;
};
