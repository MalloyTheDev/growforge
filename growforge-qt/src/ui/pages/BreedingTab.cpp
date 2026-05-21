#include "ui/pages/BreedingTab.h"
#include "ui/MainWindow.h"
#include "ui/Toast.h"
#include "ui/widgets/CommonWidgets.h"
#include "ui/widgets/Icons.h"
#include "ui/dialogs/BreedingDialogs.h"
#include "app/Theme.h"
#include "data/Database.h"

#include <QPushButton>
#include <QHBoxLayout>
#include <QVBoxLayout>
#include <QLabel>

BreedingTab::BreedingTab(MainWindow *main) : ScrollPage(main) {}

void BreedingTab::refresh() {
    auto *root = resetContent();

    auto *addBtn = new QPushButton("  New Cross");
    addBtn->setProperty("variant", "primary");
    addBtn->setIcon(Icons::icon("plus", 14, QColor("#07110b")));
    connect(addBtn, &QPushButton::clicked, this, [this]() { newCross(); });
    root->addWidget(makePageHeader("Breeding Lab",
        "Crosses, seed stock, and phenotype hunting.", addBtn));

    const Rows crosses = Db::getCrosses();
    if (crosses.isEmpty()) {
        auto *empty = new Card();
        empty->addWidget(makeMuted("No crosses yet. Record your first cross to start a breeding project."));
        root->addWidget(empty);
        root->addStretch();
        return;
    }

    for (const Row &x : crosses) {
        const int crossId = M::i(x, "id");
        auto *card = new Card(M::s(x, "cross_name"));
        card->setHeaderRight(makeBadge(M::s(x, "generation", "F1"), Tone::Violet));

        const QString parents = QString("%1  ×  %2")
            .arg(M::s(x, "mother_strain", "?"), M::s(x, "father_strain", "?"));
        auto *pl = new QLabel(parents);
        pl->setStyleSheet(QString("color:%1; font-family:'%2'; font-size:13px;")
                              .arg(Theme::current().fg0, Theme::monoFamily()));
        card->addWidget(pl);
        card->addWidget(makeKeyValue("Seeds", QString::number(M::i(x, "seed_count"))));
        card->addWidget(makeKeyValue("Pollinated", M::s(x, "pollination_date", "—")));
        if (!M::s(x, "goals").isEmpty())
            card->addWidget(makeKeyValue("Goals", M::s(x, "goals")));

        card->addWidget(hLine());
        auto *phHead = new QHBoxLayout;
        phHead->addWidget(makeSectionTitle("Phenotypes"));
        phHead->addStretch();
        auto *addPh = new QPushButton("  Add Phenotype");
        addPh->setFixedHeight(26);
        addPh->setIcon(Icons::icon("plus", 12, QColor(Theme::current().fg1)));
        connect(addPh, &QPushButton::clicked, this, [this, crossId]() { addPhenotype(crossId); });
        phHead->addWidget(addPh);
        card->addLayout(phHead);

        const Rows phenos = Db::getPhenotypes(crossId);
        if (phenos.isEmpty()) {
            card->addWidget(makeMuted("No phenotypes scored yet."));
        } else {
            for (const Row &ph : phenos) {
                auto *w = new QWidget;
                auto *r = new QHBoxLayout(w);
                r->setContentsMargins(0, 4, 0, 4);
                auto *nm = new QLabel(M::s(ph, "pheno_name"));
                nm->setStyleSheet(QString("color:%1; font-weight:600;").arg(Theme::current().fg0));
                r->addWidget(nm);
                if (M::b(ph, "is_keeper")) r->addWidget(makeBadge("Keeper", Tone::Accent));
                r->addStretch();
                auto *score = new QLabel(QString("%1 / 10").arg(M::d(ph, "overall_score"), 0, 'f', 1));
                score->setStyleSheet(QString("color:%1; font-family:'%2'; font-weight:600;")
                                         .arg(Theme::current().accent, Theme::monoFamily()));
                r->addWidget(score);
                card->addWidget(w);
            }
        }
        root->addWidget(card);
    }
    root->addStretch();
}

void BreedingTab::newCross() {
    CrossDialog dlg(this);
    if (dlg.exec() != QDialog::Accepted) return;
    Db::insertRow("crosses", dlg.data());
    Toast::show(this, "Cross recorded.", Toast::Success);
    refresh();
}

void BreedingTab::addPhenotype(int crossId) {
    PhenotypeDialog dlg(crossId, this);
    if (dlg.exec() != QDialog::Accepted) return;
    Db::insertRow("phenotypes", dlg.data());
    Toast::show(this, "Phenotype scored.", Toast::Success);
    refresh();
}
