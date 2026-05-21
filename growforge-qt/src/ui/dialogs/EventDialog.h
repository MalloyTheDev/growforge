#pragma once

#include "data/Models.h"
#include <QDialog>

class QLineEdit;
class QComboBox;
class QPlainTextEdit;
class QDateEdit;
class QLabel;

// Log a grow-journal event for a plant. Numeric readings are optional.
class EventDialog : public QDialog {
    Q_OBJECT
public:
    explicit EventDialog(int plantId, const QString &plantName,
                         const QString &defaultType = "Observation",
                         QWidget *parent = nullptr);
    Row data() const;

private slots:
    void onAccept();

private:
    int m_plantId = -1;
    QComboBox *m_type = nullptr;
    QDateEdit *m_date = nullptr;
    QLineEdit *m_title = nullptr;
    QPlainTextEdit *m_notes = nullptr;
    QLineEdit *m_ph = nullptr, *m_ec = nullptr, *m_ppm = nullptr;
    QLineEdit *m_temp = nullptr, *m_rh = nullptr, *m_vpd = nullptr, *m_water = nullptr;
    QLineEdit *m_mix = nullptr;
    QLabel *m_error = nullptr;
};
