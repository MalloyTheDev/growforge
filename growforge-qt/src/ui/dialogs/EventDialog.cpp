#include "ui/dialogs/EventDialog.h"
#include "ui/Helpers.h"
#include "core/VpdCalculator.h"
#include "app/Config.h"

#include <QFormLayout>
#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QLineEdit>
#include <QComboBox>
#include <QPlainTextEdit>
#include <QDateEdit>
#include <QLabel>
#include <QDialogButtonBox>
#include <QPushButton>
#include <QDoubleValidator>
#include <QDateTime>

static QLineEdit *numField(const QString &placeholder) {
    auto *e = new QLineEdit;
    e->setPlaceholderText(placeholder);
    auto *v = new QDoubleValidator(e);
    v->setNotation(QDoubleValidator::StandardNotation);
    e->setValidator(v);
    e->setMaximumWidth(110);
    return e;
}

EventDialog::EventDialog(int plantId, const QString &plantName,
                         const QString &defaultType, QWidget *parent)
    : QDialog(parent), m_plantId(plantId) {
    setWindowTitle("Log Event — " + plantName);
    setModal(true);
    setMinimumWidth(460);

    auto *outer = new QVBoxLayout(this);
    auto *form = new QFormLayout;
    form->setSpacing(10);

    m_type = new QComboBox;
    m_type->addItems(Config::EVENT_TYPES);
    m_type->setCurrentText(defaultType);

    m_date = new QDateEdit(QDate::currentDate());
    m_date->setCalendarPopup(true);
    m_date->setDisplayFormat("yyyy-MM-dd");

    m_title = new QLineEdit;
    m_title->setPlaceholderText("Short title (optional)");
    m_notes = new QPlainTextEdit;
    m_notes->setFixedHeight(70);
    m_notes->setPlaceholderText("What happened?");

    form->addRow("Type", m_type);
    form->addRow("Date", m_date);
    form->addRow("Title", m_title);
    form->addRow("Notes", m_notes);
    outer->addLayout(form);

    auto *readLbl = new QLabel("READINGS (optional)");
    readLbl->setObjectName("SectionTitle");
    outer->addWidget(readLbl);

    m_ph = numField("pH"); m_ec = numField("EC"); m_ppm = numField("PPM");
    m_temp = numField("Temp °C"); m_rh = numField("RH %");
    m_vpd = numField("VPD kPa"); m_water = numField("Water ml");

    auto *r1 = new QHBoxLayout;
    r1->addWidget(new QLabel("pH"));    r1->addWidget(m_ph);
    r1->addWidget(new QLabel("EC"));    r1->addWidget(m_ec);
    r1->addWidget(new QLabel("PPM"));   r1->addWidget(m_ppm);
    r1->addStretch();
    outer->addLayout(r1);
    auto *r2 = new QHBoxLayout;
    r2->addWidget(new QLabel("Temp"));  r2->addWidget(m_temp);
    r2->addWidget(new QLabel("RH"));    r2->addWidget(m_rh);
    r2->addWidget(new QLabel("VPD"));   r2->addWidget(m_vpd);
    r2->addStretch();
    outer->addLayout(r2);
    auto *r3 = new QHBoxLayout;
    r3->addWidget(new QLabel("Water ml")); r3->addWidget(m_water);
    m_mix = new QLineEdit; m_mix->setPlaceholderText("Nutrient mix (optional)");
    r3->addWidget(m_mix, 1);
    outer->addLayout(r3);

    // Auto-fill VPD when temp + RH are present.
    auto autoVpd = [this]() {
        bool okT = false, okH = false;
        double t = m_temp->text().toDouble(&okT);
        double h = m_rh->text().toDouble(&okH);
        if (okT && okH && m_vpd->text().isEmpty())
            m_vpd->setText(QString::number(Vpd::calc(t, h)));
    };
    connect(m_temp, &QLineEdit::editingFinished, this, autoVpd);
    connect(m_rh, &QLineEdit::editingFinished, this, autoVpd);

    m_error = new QLabel; m_error->setVisible(false);
    outer->addWidget(m_error);

    auto *bb = new QDialogButtonBox(QDialogButtonBox::Save | QDialogButtonBox::Cancel);
    bb->button(QDialogButtonBox::Save)->setProperty("variant", "primary");
    connect(bb, &QDialogButtonBox::accepted, this, &EventDialog::onAccept);
    connect(bb, &QDialogButtonBox::rejected, this, &QDialog::reject);
    outer->addWidget(bb);
}

void EventDialog::onAccept() {
    if (m_notes->toPlainText().trimmed().isEmpty() && m_title->text().trimmed().isEmpty()) {
        Validate::showError(m_error, "Add a title or some notes.");
        return;
    }
    accept();
}

Row EventDialog::data() const {
    Row r;
    r["plant_id"] = m_plantId;
    r["event_type"] = m_type->currentText();
    // Combine the picked date with the current time — QDate alone would emit a
    // literal "HH:mm:ss" and corrupt event ordering.
    r["event_date"] = QDateTime(m_date->date(), QTime::currentTime())
                          .toString("yyyy-MM-dd HH:mm:ss");
    r["title"] = m_title->text().trimmed();
    r["notes"] = m_notes->toPlainText().trimmed();
    auto addNum = [&](const QString &key, QLineEdit *e) {
        bool ok = false; double v = e->text().toDouble(&ok);
        if (ok && !e->text().isEmpty()) r[key] = v;
    };
    addNum("ph", m_ph); addNum("ec", m_ec); addNum("ppm", m_ppm);
    addNum("temp", m_temp); addNum("humidity", m_rh);
    addNum("vpd", m_vpd); addNum("water_ml", m_water);
    if (!m_mix->text().trimmed().isEmpty()) r["nutrient_mix"] = m_mix->text().trimmed();
    return r;
}
