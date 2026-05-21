#include "ui/dialogs/BreedingDialogs.h"
#include "ui/Helpers.h"
#include "app/Config.h"
#include "data/Database.h"

#include <QFormLayout>
#include <QVBoxLayout>
#include <QGridLayout>
#include <QLineEdit>
#include <QComboBox>
#include <QSpinBox>
#include <QCheckBox>
#include <QPlainTextEdit>
#include <QDateEdit>
#include <QLabel>
#include <QDialogButtonBox>
#include <QPushButton>

// ─── CrossDialog ─────────────────────────────────────────────────────────────
CrossDialog::CrossDialog(QWidget *parent) : QDialog(parent) {
    setWindowTitle("New Cross");
    setModal(true);
    setMinimumWidth(460);

    auto *outer = new QVBoxLayout(this);
    auto *form = new QFormLayout;
    form->setSpacing(10);

    m_name = new QLineEdit; m_name->setPlaceholderText("e.g. Blue Cookies");
    m_mother = new QComboBox; m_mother->addItem("None", -1);
    m_father = new QComboBox; m_father->addItem("None", -1);
    for (const Row &p : Db::getAll("plants", "is_active=1", {}, "name ASC")) {
        m_mother->addItem(M::s(p, "name"), M::i(p, "id"));
        m_father->addItem(M::s(p, "name"), M::i(p, "id"));
    }
    m_motherStrain = new QLineEdit; m_motherStrain->setPlaceholderText("Mother strain");
    m_fatherStrain = new QLineEdit; m_fatherStrain->setPlaceholderText("Father strain");
    m_pollDate = new QDateEdit(QDate::currentDate());
    m_pollDate->setCalendarPopup(true); m_pollDate->setDisplayFormat("yyyy-MM-dd");
    m_seeds = new QSpinBox; m_seeds->setRange(0, 100000);
    m_gen = new QComboBox; m_gen->addItems({"F1", "F2", "F3", "F4+", "BX1", "S1"});
    m_goals = new QLineEdit; m_goals->setPlaceholderText("Breeding goals");
    m_notes = new QPlainTextEdit; m_notes->setFixedHeight(60);

    form->addRow("Cross name", m_name);
    form->addRow("Mother plant", m_mother);
    form->addRow("Father plant", m_father);
    form->addRow("Mother strain", m_motherStrain);
    form->addRow("Father strain", m_fatherStrain);
    form->addRow("Pollination", m_pollDate);
    form->addRow("Seed count", m_seeds);
    form->addRow("Generation", m_gen);
    form->addRow("Goals", m_goals);
    form->addRow("Notes", m_notes);
    outer->addLayout(form);

    m_error = new QLabel; m_error->setVisible(false);
    outer->addWidget(m_error);

    auto *bb = new QDialogButtonBox(QDialogButtonBox::Save | QDialogButtonBox::Cancel);
    bb->button(QDialogButtonBox::Save)->setProperty("variant", "primary");
    connect(bb, &QDialogButtonBox::accepted, this, &CrossDialog::onAccept);
    connect(bb, &QDialogButtonBox::rejected, this, &QDialog::reject);
    outer->addWidget(bb);
}

void CrossDialog::onAccept() {
    if (!Validate::notEmpty(m_name->text())) {
        Validate::showError(m_error, "Cross name is required.");
        return;
    }
    accept();
}

Row CrossDialog::data() const {
    Row r;
    r["cross_name"] = m_name->text().trimmed();
    const int mid = m_mother->currentData().toInt();
    const int fid = m_father->currentData().toInt();
    if (mid >= 0) r["mother_plant_id"] = mid;
    if (fid >= 0) r["father_plant_id"] = fid;
    r["mother_strain"] = m_motherStrain->text().trimmed();
    r["father_strain"] = m_fatherStrain->text().trimmed();
    r["pollination_date"] = m_pollDate->date().toString("yyyy-MM-dd");
    r["seed_count"] = m_seeds->value();
    r["generation"] = m_gen->currentText();
    r["goals"] = m_goals->text().trimmed();
    r["notes"] = m_notes->toPlainText().trimmed();
    return r;
}

// ─── PhenotypeDialog ─────────────────────────────────────────────────────────
PhenotypeDialog::PhenotypeDialog(int crossId, QWidget *parent)
    : QDialog(parent), m_crossId(crossId) {
    setWindowTitle("Score Phenotype");
    setModal(true);
    setMinimumWidth(440);

    m_scoreCols = {
        "vigor_score", "structure_score", "yield_score", "terpene_score",
        "resin_score", "pest_resistance_score", "mold_resistance_score",
        "bag_appeal_score", "potency_score", "flavor_score",
    };

    auto *outer = new QVBoxLayout(this);
    auto *top = new QFormLayout;
    m_name = new QLineEdit; m_name->setPlaceholderText("e.g. Blue Cookies #7");
    top->addRow("Phenotype name", m_name);
    outer->addLayout(top);

    auto *grid = new QGridLayout;
    int r = 0, c = 0;
    for (int i = 0; i < Config::PHENO_SCORE_CATEGORIES.size(); ++i) {
        auto *box = new QVBoxLayout;
        auto *lab = new QLabel(Config::PHENO_SCORE_CATEGORIES[i]);
        auto *sp = new QSpinBox; sp->setRange(1, 10); sp->setValue(5);
        m_scores << sp;
        box->addWidget(lab);
        box->addWidget(sp);
        auto *cell = new QWidget; cell->setLayout(box);
        grid->addWidget(cell, r, c);
        if (++c >= 2) { c = 0; ++r; }
    }
    outer->addLayout(grid);

    auto *bottom = new QFormLayout;
    m_flowerDays = new QSpinBox; m_flowerDays->setRange(0, 365);
    m_keeper = new QCheckBox("Keeper");
    m_notes = new QPlainTextEdit; m_notes->setFixedHeight(56);
    bottom->addRow("Flowering days", m_flowerDays);
    bottom->addRow("", m_keeper);
    bottom->addRow("Notes", m_notes);
    outer->addLayout(bottom);

    m_error = new QLabel; m_error->setVisible(false);
    outer->addWidget(m_error);

    auto *bb = new QDialogButtonBox(QDialogButtonBox::Save | QDialogButtonBox::Cancel);
    bb->button(QDialogButtonBox::Save)->setProperty("variant", "primary");
    connect(bb, &QDialogButtonBox::accepted, this, &PhenotypeDialog::onAccept);
    connect(bb, &QDialogButtonBox::rejected, this, &QDialog::reject);
    outer->addWidget(bb);
}

void PhenotypeDialog::onAccept() {
    if (!Validate::notEmpty(m_name->text())) {
        Validate::showError(m_error, "Phenotype name is required.");
        return;
    }
    accept();
}

Row PhenotypeDialog::data() const {
    Row r;
    r["cross_id"] = m_crossId;
    r["pheno_name"] = m_name->text().trimmed();
    for (int i = 0; i < m_scoreCols.size(); ++i)
        r[m_scoreCols[i]] = m_scores[i]->value();
    r["flowering_days"] = m_flowerDays->value();
    r["is_keeper"] = m_keeper->isChecked() ? 1 : 0;
    r["notes"] = m_notes->toPlainText().trimmed();
    return r;   // overall_score auto-calculated by Db::insertRow
}
