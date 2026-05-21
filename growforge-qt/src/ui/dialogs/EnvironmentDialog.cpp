#include "ui/dialogs/EnvironmentDialog.h"
#include "ui/Helpers.h"
#include "app/Config.h"

#include <QFormLayout>
#include <QVBoxLayout>
#include <QLineEdit>
#include <QComboBox>
#include <QSpinBox>
#include <QPlainTextEdit>
#include <QLabel>
#include <QDialogButtonBox>
#include <QPushButton>

EnvironmentDialog::EnvironmentDialog(const Row &existing, QWidget *parent)
    : QDialog(parent) {
    const bool editing = !existing.isEmpty();
    m_id = editing ? M::i(existing, "id", -1) : -1;
    setWindowTitle(editing ? "Edit Environment" : "Add Environment");
    setModal(true);
    setMinimumWidth(440);

    auto *outer = new QVBoxLayout(this);
    auto *form = new QFormLayout;
    form->setSpacing(10);

    m_name = new QLineEdit(M::s(existing, "name"));
    m_name->setPlaceholderText("e.g. Main Tent");

    m_type = new QComboBox;
    m_type->setEditable(true);
    m_type->addItems({"Indoor Tent", "Cabinet", "Grow Room", "Greenhouse", "Outdoor"});
    m_type->setCurrentText(M::s(existing, "env_type", "Indoor Tent"));

    m_medium = new QComboBox;
    m_medium->addItems(Config::MEDIUMS);
    m_medium->setCurrentText(M::s(existing, "medium", "Soil (Organic)"));

    m_lightType = new QComboBox;
    m_lightType->addItems(Config::LIGHT_TYPES);
    m_lightType->setCurrentText(M::s(existing, "light_type", "LED (Full Spectrum)"));

    m_watts = new QSpinBox;
    m_watts->setRange(0, 100000);
    m_watts->setSuffix(" W");
    m_watts->setValue(M::i(existing, "light_wattage"));

    m_schedule = new QLineEdit(M::s(existing, "light_schedule", "18/6"));
    m_tentSize = new QLineEdit(M::s(existing, "tent_size"));
    m_tentSize->setPlaceholderText("e.g. 4x4 ft");

    m_notes = new QPlainTextEdit(M::s(existing, "notes"));
    m_notes->setFixedHeight(70);

    form->addRow("Name", m_name);
    form->addRow("Type", m_type);
    form->addRow("Medium", m_medium);
    form->addRow("Light type", m_lightType);
    form->addRow("Wattage", m_watts);
    form->addRow("Light schedule", m_schedule);
    form->addRow("Tent size", m_tentSize);
    form->addRow("Notes", m_notes);
    outer->addLayout(form);

    m_error = new QLabel;
    m_error->setVisible(false);
    outer->addWidget(m_error);

    auto *bb = new QDialogButtonBox(QDialogButtonBox::Save | QDialogButtonBox::Cancel);
    bb->button(QDialogButtonBox::Save)->setProperty("variant", "primary");
    connect(bb, &QDialogButtonBox::accepted, this, &EnvironmentDialog::onAccept);
    connect(bb, &QDialogButtonBox::rejected, this, &QDialog::reject);
    outer->addWidget(bb);
}

void EnvironmentDialog::onAccept() {
    if (!Validate::notEmpty(m_name->text())) {
        Validate::showError(m_error, "Name is required.");
        return;
    }
    accept();
}

Row EnvironmentDialog::data() const {
    Row r;
    r["name"] = m_name->text().trimmed();
    r["env_type"] = m_type->currentText().trimmed();
    r["medium"] = m_medium->currentText();
    r["light_type"] = m_lightType->currentText();
    r["light_wattage"] = m_watts->value();
    r["light_schedule"] = m_schedule->text().trimmed();
    r["tent_size"] = m_tentSize->text().trimmed();
    r["notes"] = m_notes->toPlainText().trimmed();
    return r;
}
