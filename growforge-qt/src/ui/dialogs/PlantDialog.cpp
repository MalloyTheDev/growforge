#include "ui/dialogs/PlantDialog.h"
#include "ui/Helpers.h"
#include "app/Config.h"
#include "data/Database.h"
#include "data/KnowledgeBase.h"

#include <QFormLayout>
#include <QVBoxLayout>
#include <QLineEdit>
#include <QComboBox>
#include <QPlainTextEdit>
#include <QDateEdit>
#include <QCheckBox>
#include <QLabel>
#include <QDialogButtonBox>
#include <QPushButton>
#include <QCompleter>

PlantDialog::PlantDialog(const Row &existing, QWidget *parent) : QDialog(parent) {
    const bool editing = !existing.isEmpty();
    m_id = editing ? M::i(existing, "id", -1) : -1;
    setWindowTitle(editing ? "Edit Plant" : "Add Plant");
    setModal(true);
    setMinimumWidth(460);

    auto *outer = new QVBoxLayout(this);
    auto *form = new QFormLayout;
    form->setSpacing(10);

    m_name = new QLineEdit(M::s(existing, "name"));
    m_name->setPlaceholderText("e.g. Blue Dream #1");

    m_strain = new QComboBox;
    m_strain->setEditable(true);
    m_strain->setInsertPolicy(QComboBox::NoInsert);   // typing a custom strain won't mutate the list
    m_strain->setMaxVisibleItems(20);
    m_strain->addItem("");
    m_strain->addItems(KB::strainNames());            // 2,300+ entries
    m_strain->setCurrentText(M::s(existing, "strain_name"));
    // Make the large library searchable: type any fragment, case-insensitive.
    if (QCompleter *c = m_strain->completer()) {
        c->setCompletionMode(QCompleter::PopupCompletion);
        c->setCaseSensitivity(Qt::CaseInsensitive);
        c->setFilterMode(Qt::MatchContains);
    }

    m_plantType = new QComboBox;
    m_plantType->addItems(Config::PLANT_TYPES);
    m_plantType->setCurrentText(M::s(existing, "plant_type", "Photoperiod"));

    m_genetics = new QComboBox;
    m_genetics->addItems(Config::GENETICS_TYPES);
    m_genetics->setCurrentText(M::s(existing, "genetics_type", "Feminized"));

    m_stage = new QComboBox;
    m_stage->addItems(Config::STAGES);
    m_stage->setCurrentText(M::s(existing, "stage", "Germination"));

    m_env = new QComboBox;
    m_env->addItem("None", -1);
    for (const Row &e : Db::getAll("environments", QString(), {}, "name ASC"))
        m_env->addItem(M::s(e, "name"), M::i(e, "id"));
    if (editing) {
        int idx = m_env->findData(M::i(existing, "environment_id", -1));
        m_env->setCurrentIndex(idx >= 0 ? idx : 0);
    }

    m_medium = new QComboBox;
    m_medium->addItem("");
    m_medium->addItems(Config::MEDIUMS);
    m_medium->setCurrentText(M::s(existing, "medium"));

    m_pot = new QLineEdit(M::s(existing, "pot_size"));
    m_pot->setPlaceholderText("e.g. 5 gallon");

    m_start = new QDateEdit;
    m_start->setCalendarPopup(true);
    m_start->setDisplayFormat("yyyy-MM-dd");
    {
        QDate d = QDate::fromString(M::s(existing, "start_date").left(10), "yyyy-MM-dd");
        m_start->setDate(d.isValid() ? d : QDate::currentDate());
    }

    m_mother = new QCheckBox("This is a mother plant");
    m_mother->setChecked(M::b(existing, "is_mother"));

    m_notes = new QPlainTextEdit(M::s(existing, "notes"));
    m_notes->setFixedHeight(70);

    form->addRow("Name", m_name);
    form->addRow("Strain", m_strain);
    form->addRow("Type", m_plantType);
    form->addRow("Genetics", m_genetics);
    form->addRow("Stage", m_stage);
    form->addRow("Environment", m_env);
    form->addRow("Medium", m_medium);
    form->addRow("Pot size", m_pot);
    form->addRow("Start date", m_start);
    form->addRow("", m_mother);
    form->addRow("Notes", m_notes);
    outer->addLayout(form);

    m_error = new QLabel; m_error->setVisible(false);
    outer->addWidget(m_error);

    auto *bb = new QDialogButtonBox(QDialogButtonBox::Save | QDialogButtonBox::Cancel);
    bb->button(QDialogButtonBox::Save)->setProperty("variant", "primary");
    connect(bb, &QDialogButtonBox::accepted, this, &PlantDialog::onAccept);
    connect(bb, &QDialogButtonBox::rejected, this, &QDialog::reject);
    outer->addWidget(bb);
}

void PlantDialog::onAccept() {
    if (!Validate::notEmpty(m_name->text())) {
        Validate::showError(m_error, "Plant name is required.");
        return;
    }
    accept();
}

Row PlantDialog::data() const {
    Row r;
    r["name"] = m_name->text().trimmed();
    const QString strain = m_strain->currentText().trimmed();
    r["strain_name"] = strain;
    // Resolve strain_id if the name matches a library/DB strain.
    if (!strain.isEmpty()) {
        const Rows m = Db::getAll("strains", "name=?", {strain});
        if (!m.isEmpty()) r["strain_id"] = M::i(m.first(), "id");
    }
    r["plant_type"] = m_plantType->currentText();
    r["genetics_type"] = m_genetics->currentText();
    r["stage"] = m_stage->currentText();
    const int envId = m_env->currentData().toInt();
    r["environment_id"] = envId >= 0 ? QVariant(envId) : QVariant();
    r["medium"] = m_medium->currentText();
    r["pot_size"] = m_pot->text().trimmed();
    r["start_date"] = m_start->date().toString("yyyy-MM-dd");
    r["is_mother"] = m_mother->isChecked() ? 1 : 0;
    r["notes"] = m_notes->toPlainText().trimmed();
    r["is_active"] = 1;
    return r;
}
