#include "ui/dialogs/CloneBatchDialog.h"
#include "ui/Helpers.h"
#include "app/Config.h"
#include "data/Database.h"

#include <QFormLayout>
#include <QVBoxLayout>
#include <QLineEdit>
#include <QComboBox>
#include <QSpinBox>
#include <QPlainTextEdit>
#include <QDateEdit>
#include <QLabel>
#include <QDialogButtonBox>
#include <QPushButton>

CloneBatchDialog::CloneBatchDialog(QWidget *parent) : QDialog(parent) {
    setWindowTitle("New Clone Batch");
    setModal(true);
    setMinimumWidth(440);

    auto *outer = new QVBoxLayout(this);
    auto *form = new QFormLayout;
    form->setSpacing(10);

    m_mother = new QComboBox;
    for (const Row &m : Db::getMotherPlants())
        m_mother->addItem(M::s(m, "name"), M::i(m, "id"));
    m_hasMothers = m_mother->count() > 0;
    if (!m_hasMothers) m_mother->addItem("No mother plants — mark one in Plants", -1);

    m_name = new QLineEdit;
    m_name->setPlaceholderText("e.g. GSC Batch #4");
    m_cutDate = new QDateEdit(QDate::currentDate());
    m_cutDate->setCalendarPopup(true);
    m_cutDate->setDisplayFormat("yyyy-MM-dd");
    m_rooting = new QComboBox; m_rooting->addItems(Config::ROOTING_METHODS);
    m_medium = new QComboBox; m_medium->addItems(Config::MEDIUMS);
    m_cuts = new QSpinBox; m_cuts->setRange(1, 200); m_cuts->setValue(6);
    m_notes = new QPlainTextEdit; m_notes->setFixedHeight(64);

    form->addRow("Mother plant", m_mother);
    form->addRow("Batch name", m_name);
    form->addRow("Cut date", m_cutDate);
    form->addRow("Rooting method", m_rooting);
    form->addRow("Medium", m_medium);
    form->addRow("Number of cuts", m_cuts);
    form->addRow("Notes", m_notes);
    outer->addLayout(form);

    m_error = new QLabel; m_error->setVisible(false);
    outer->addWidget(m_error);

    auto *bb = new QDialogButtonBox(QDialogButtonBox::Save | QDialogButtonBox::Cancel);
    bb->button(QDialogButtonBox::Save)->setProperty("variant", "primary");
    bb->button(QDialogButtonBox::Save)->setEnabled(m_hasMothers);
    connect(bb, &QDialogButtonBox::accepted, this, &CloneBatchDialog::onAccept);
    connect(bb, &QDialogButtonBox::rejected, this, &QDialog::reject);
    outer->addWidget(bb);
}

void CloneBatchDialog::onAccept() {
    if (!Validate::notEmpty(m_name->text())) {
        Validate::showError(m_error, "Batch name is required.");
        return;
    }
    accept();
}

int CloneBatchDialog::numCuts() const { return m_cuts->value(); }
QString CloneBatchDialog::batchName() const { return m_name->text().trimmed(); }

Row CloneBatchDialog::data() const {
    Row r;
    r["mother_plant_id"] = m_mother->currentData().toInt();
    r["batch_name"] = m_name->text().trimmed();
    r["cut_date"] = m_cutDate->date().toString("yyyy-MM-dd");
    r["rooting_method"] = m_rooting->currentText();
    r["medium"] = m_medium->currentText();
    r["num_cuts"] = m_cuts->value();
    r["notes"] = m_notes->toPlainText().trimmed();
    return r;
}
