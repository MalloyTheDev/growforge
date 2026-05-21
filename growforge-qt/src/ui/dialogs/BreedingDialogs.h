#pragma once

#include "data/Models.h"
#include <QDialog>
#include <QList>

class QLineEdit;
class QComboBox;
class QSpinBox;
class QCheckBox;
class QPlainTextEdit;
class QDateEdit;
class QLabel;

// Create a breeding cross.
class CrossDialog : public QDialog {
    Q_OBJECT
public:
    explicit CrossDialog(QWidget *parent = nullptr);
    Row data() const;

private slots:
    void onAccept();

private:
    QLineEdit *m_name = nullptr;
    QComboBox *m_mother = nullptr;
    QComboBox *m_father = nullptr;
    QLineEdit *m_motherStrain = nullptr;
    QLineEdit *m_fatherStrain = nullptr;
    QDateEdit *m_pollDate = nullptr;
    QSpinBox *m_seeds = nullptr;
    QComboBox *m_gen = nullptr;
    QLineEdit *m_goals = nullptr;
    QPlainTextEdit *m_notes = nullptr;
    QLabel *m_error = nullptr;
};

// Score a phenotype from a cross (10 categories, overall auto-calculated by DB).
class PhenotypeDialog : public QDialog {
    Q_OBJECT
public:
    explicit PhenotypeDialog(int crossId, QWidget *parent = nullptr);
    Row data() const;

private slots:
    void onAccept();

private:
    int m_crossId = -1;
    QLineEdit *m_name = nullptr;
    QList<QSpinBox *> m_scores;     // aligned with the column list
    QStringList m_scoreCols;
    QSpinBox *m_flowerDays = nullptr;
    QCheckBox *m_keeper = nullptr;
    QPlainTextEdit *m_notes = nullptr;
    QLabel *m_error = nullptr;
};
