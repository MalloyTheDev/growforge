#pragma once

#include "data/Models.h"
#include <QDialog>

class QLineEdit;
class QComboBox;
class QPlainTextEdit;
class QDateEdit;
class QCheckBox;
class QLabel;

// Add / edit a plant.
class PlantDialog : public QDialog {
    Q_OBJECT
public:
    explicit PlantDialog(const Row &existing = {}, QWidget *parent = nullptr);
    Row data() const;             // resolves strain_id + environment_id
    int editingId() const { return m_id; }

private slots:
    void onAccept();

private:
    int m_id = -1;
    QLineEdit *m_name = nullptr;
    QComboBox *m_strain = nullptr;
    QComboBox *m_plantType = nullptr;
    QComboBox *m_genetics = nullptr;
    QComboBox *m_stage = nullptr;
    QComboBox *m_env = nullptr;
    QComboBox *m_medium = nullptr;
    QLineEdit *m_pot = nullptr;
    QDateEdit *m_start = nullptr;
    QCheckBox *m_mother = nullptr;
    QPlainTextEdit *m_notes = nullptr;
    QLabel *m_error = nullptr;
};
