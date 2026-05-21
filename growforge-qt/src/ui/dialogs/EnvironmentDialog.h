#pragma once

#include "data/Models.h"
#include <QDialog>

class QLineEdit;
class QComboBox;
class QSpinBox;
class QPlainTextEdit;
class QLabel;

// Add / edit an environment (tent / room).
class EnvironmentDialog : public QDialog {
    Q_OBJECT
public:
    explicit EnvironmentDialog(const Row &existing = {}, QWidget *parent = nullptr);
    Row data() const;          // collected field values
    int editingId() const { return m_id; }

private slots:
    void onAccept();

private:
    int m_id = -1;
    QLineEdit *m_name = nullptr;
    QComboBox *m_type = nullptr;
    QComboBox *m_medium = nullptr;
    QComboBox *m_lightType = nullptr;
    QSpinBox *m_watts = nullptr;
    QLineEdit *m_schedule = nullptr;
    QLineEdit *m_tentSize = nullptr;
    QPlainTextEdit *m_notes = nullptr;
    QLabel *m_error = nullptr;
};
