#pragma once

#include "data/Models.h"
#include <QDialog>

class QLineEdit;
class QComboBox;
class QSpinBox;
class QPlainTextEdit;
class QDateEdit;
class QLabel;

// Create a clone batch (and its individual cuts).
class CloneBatchDialog : public QDialog {
    Q_OBJECT
public:
    explicit CloneBatchDialog(QWidget *parent = nullptr);
    bool hasMothers() const { return m_hasMothers; }
    Row data() const;            // clone_batches row
    int numCuts() const;
    QString batchName() const;

private slots:
    void onAccept();

private:
    bool m_hasMothers = false;
    QComboBox *m_mother = nullptr;
    QLineEdit *m_name = nullptr;
    QDateEdit *m_cutDate = nullptr;
    QComboBox *m_rooting = nullptr;
    QComboBox *m_medium = nullptr;
    QSpinBox *m_cuts = nullptr;
    QPlainTextEdit *m_notes = nullptr;
    QLabel *m_error = nullptr;
};
