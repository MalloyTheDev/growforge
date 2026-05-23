#include "ui/pages/CloningTab.h"
#include "ui/MainWindow.h"
#include "ui/Toast.h"
#include "ui/widgets/CommonWidgets.h"
#include "ui/widgets/Icons.h"
#include "ui/dialogs/CloneBatchDialog.h"
#include "app/Config.h"
#include "app/Theme.h"
#include "data/Database.h"

#include <QPushButton>
#include <QHBoxLayout>
#include <QVBoxLayout>
#include <QLabel>
#include <QDateTime>

CloningTab::CloningTab(MainWindow *main) : ScrollPage(main) {}

static Tone::T cloneTone(const QString &status) {
    if (status == "Dead") return Tone::Crit;
    if (status == "Promoted") return Tone::Accent;
    return Tone::Cool;
}

QWidget *CloningTab::cloneRow(const Row &clone, const Row &batch) {
    auto *w = new QWidget;
    auto *r = new QHBoxLayout(w);
    r->setContentsMargins(0, 4, 0, 4);
    r->setSpacing(8);
    auto *name = new QLabel(M::s(clone, "clone_name"));
    name->setTextFormat(Qt::PlainText);
    name->setStyleSheet(QString("color:%1;").arg(Theme::current().fg1));
    r->addWidget(name);
    r->addWidget(makeStageBadge(M::s(clone, "stage")));
    r->addWidget(makeBadge(M::s(clone, "status"), cloneTone(M::s(clone, "status"))));
    r->addStretch();

    const QString status = M::s(clone, "status");
    if (status == "Active") {
        auto *adv = new QPushButton("Advance");
        adv->setFixedHeight(26);
        connect(adv, &QPushButton::clicked, this, [this, clone]() { advanceClone(clone); });
        r->addWidget(adv);
        const QString stage = M::s(clone, "stage");
        if (stage == "Rooted" || stage == "Transplanted") {
            auto *prom = new QPushButton("Promote");
            prom->setProperty("variant", "primary");
            prom->setFixedHeight(26);
            connect(prom, &QPushButton::clicked, this, [this, clone, batch]() { promoteClone(clone, batch); });
            r->addWidget(prom);
        }
    }
    return w;
}

void CloningTab::refresh() {
    auto *root = resetContent();

    auto *addBtn = new QPushButton("  New Batch");
    addBtn->setProperty("variant", "primary");
    addBtn->setIcon(Icons::icon("plus", 14, QColor("#07110b")));
    connect(addBtn, &QPushButton::clicked, this, [this]() { newBatch(); });
    root->addWidget(makePageHeader("Cloning Station",
        "Mother plants, clone batches, and rooting progress.", addBtn));

    const Rows mothers = Db::getMotherPlants();
    auto *motherCard = new Card(QString("Mother Plants (%1)").arg(mothers.size()));
    if (mothers.isEmpty()) {
        motherCard->addWidget(makeMuted("No mother plants. Mark a plant as a mother in the Plants screen."));
    } else {
        int n = 0;
        for (const Row &m : mothers) {
            if (n++) motherCard->addWidget(hLine());
            motherCard->addWidget(makeKeyValue(M::s(m, "name"),
                M::s(m, "strain_name", "—") + "  ·  Day " + QString::number(M::daysSince(M::s(m, "start_date")))));
        }
    }
    root->addWidget(motherCard);

    const Rows batches = Db::getCloneBatches();
    if (batches.isEmpty()) {
        auto *empty = new Card("Clone Batches");
        empty->addWidget(makeMuted("No clone batches yet. Create one to start tracking cuttings."));
        root->addWidget(empty);
        root->addStretch();
        return;
    }

    for (const Row &b : batches) {
        const Row mother = Db::getRow("plants", M::i(b, "mother_plant_id"));
        auto *card = new Card(M::s(b, "batch_name"));
        card->setHeaderRight(makeBadge(M::s(b, "rooting_method"), Tone::Muted));
        card->addWidget(makeKeyValue("Mother", M::s(mother, "name", "—")));
        card->addWidget(makeKeyValue("Cut date", M::s(b, "cut_date")));
        card->addWidget(makeKeyValue("Cuts", QString::number(M::i(b, "num_cuts"))));
        if (!M::s(b, "notes").isEmpty()) card->addWidget(makeMuted(M::s(b, "notes")));
        card->addWidget(hLine());
        card->addWidget(makeSectionTitle("Clones"));
        const Rows clones = Db::getClonesInBatch(M::i(b, "id"));
        if (clones.isEmpty()) card->addWidget(makeMuted("No individual clones recorded."));
        for (const Row &c : clones) card->addWidget(cloneRow(c, b));
        root->addWidget(card);
    }
    root->addStretch();
}

void CloningTab::newBatch() {
    CloneBatchDialog dlg(this);
    if (!dlg.hasMothers()) {
        Toast::show(this, "Mark a plant as a mother first (Plants → edit).", Toast::Warning, 5000);
    }
    if (dlg.exec() != QDialog::Accepted) return;
    const int batchId = Db::insertRow("clone_batches", dlg.data());
    // Create individual cuts.
    for (int i = 1; i <= dlg.numCuts(); ++i) {
        Row c;
        c["batch_id"] = batchId;
        c["clone_name"] = QString("%1 - #%2").arg(dlg.batchName()).arg(i);
        c["stage"] = "Cut Taken";
        c["status"] = "Active";
        Db::insertRow("clones", c);
    }
    Toast::show(this, "Clone batch created.", Toast::Success);
    refresh();
}

void CloningTab::advanceClone(const Row &clone) {
    const QString cur = M::s(clone, "stage");
    const int idx = Config::CLONE_STAGES.indexOf(cur);
    if (idx < 0 || idx >= Config::CLONE_STAGES.size() - 1) {
        Toast::show(this, "Clone is at the final rooting stage.", Toast::Info);
        return;
    }
    const QString next = Config::CLONE_STAGES.at(idx + 1);
    Row upd;
    upd["stage"] = next;
    upd["updated_at"] = QDateTime::currentDateTime().toString("yyyy-MM-dd HH:mm:ss");
    if (next == "Rooted") upd["root_date"] = QDate::currentDate().toString("yyyy-MM-dd");
    if (next == "Transplanted") upd["transplant_date"] = QDate::currentDate().toString("yyyy-MM-dd");
    Db::updateRow("clones", M::i(clone, "id"), upd);
    refresh();
}

void CloningTab::promoteClone(const Row &clone, const Row &batch) {
    const Row mother = Db::getRow("plants", M::i(batch, "mother_plant_id"));
    Row p;
    p["name"] = M::s(clone, "clone_name");
    p["strain_name"] = M::s(mother, "strain_name");
    p["strain_id"] = mother.value("strain_id");
    p["plant_type"] = "Photoperiod";
    p["genetics_type"] = "Clone";
    p["stage"] = "Vegetative";
    p["mother_plant_id"] = M::i(batch, "mother_plant_id");
    p["medium"] = M::s(batch, "medium");
    p["start_date"] = QDate::currentDate().toString("yyyy-MM-dd");
    p["is_active"] = 1;
    p["updated_at"] = QDateTime::currentDateTime().toString("yyyy-MM-dd HH:mm:ss");
    const int plantId = Db::insertRow("plants", p);

    Row upd;
    upd["status"] = "Promoted";
    upd["promoted_plant_id"] = plantId;
    Db::updateRow("clones", M::i(clone, "id"), upd);

    Toast::show(this, "Clone promoted to a plant.", Toast::Success);
    m_main->refreshChrome();
    refresh();
}
