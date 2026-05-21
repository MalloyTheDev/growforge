#include "ui/pages/EnvironmentsTab.h"
#include "ui/MainWindow.h"
#include "ui/Toast.h"
#include "ui/widgets/CommonWidgets.h"
#include "ui/widgets/Icons.h"
#include "ui/dialogs/EnvironmentDialog.h"
#include "app/Theme.h"
#include "data/Database.h"

#include <QPushButton>
#include <QHBoxLayout>
#include <QVBoxLayout>
#include <QGridLayout>
#include <QLabel>
#include <QMessageBox>

EnvironmentsTab::EnvironmentsTab(MainWindow *main) : ScrollPage(main) {}

void EnvironmentsTab::refresh() {
    auto *root = resetContent();

    auto *addBtn = new QPushButton("  Add Environment");
    addBtn->setProperty("variant", "primary");
    addBtn->setIcon(Icons::icon("plus", 14, QColor("#07110b")));
    connect(addBtn, &QPushButton::clicked, this, [this]() { addOrEdit({}); });
    root->addWidget(makePageHeader("Environments",
        "Tents, cabinets, and rooms where your plants live.", addBtn));

    const Rows envs = Db::getAll("environments", QString(), {}, "name ASC");
    if (envs.isEmpty()) {
        auto *empty = new Card();
        empty->addWidget(makeMuted("No environments yet. Add your first tent or room."));
        root->addWidget(empty);
        root->addStretch();
        return;
    }

    auto *grid = new QGridLayout;
    grid->setSpacing(14);
    int col = 0, rowN = 0;
    const int cols = 2;
    for (const Row &env : envs) {
        const int id = M::i(env, "id");
        const int plantCount = Db::count("plants", "environment_id=? AND is_active=1", {id});

        auto *card = new Card(M::s(env, "name"));
        auto *typeBadge = makeBadge(M::s(env, "env_type"), Tone::Cool);
        card->setHeaderRight(typeBadge);

        card->addWidget(makeKeyValue("Light",
            QString("%1 · %2W").arg(M::s(env, "light_type")).arg(M::i(env, "light_wattage"))));
        card->addWidget(makeKeyValue("Schedule", M::s(env, "light_schedule")));
        card->addWidget(makeKeyValue("Medium", M::s(env, "medium")));
        card->addWidget(makeKeyValue("Tent size", M::s(env, "tent_size", "—")));
        card->addWidget(makeKeyValue("Active plants", QString::number(plantCount)));
        if (!M::s(env, "notes").isEmpty()) {
            card->addWidget(hLine());
            card->addWidget(makeMuted(M::s(env, "notes")));
        }

        auto *actions = new QHBoxLayout;
        actions->addStretch();
        auto *editBtn = new QPushButton("  Edit");
        editBtn->setIcon(Icons::icon("edit", 13, QColor(Theme::current().fg1)));
        connect(editBtn, &QPushButton::clicked, this, [this, env]() { addOrEdit(env); });
        auto *delBtn = new QPushButton("  Delete");
        delBtn->setProperty("variant", "danger");
        delBtn->setIcon(Icons::icon("trash", 13, QColor(Theme::current().crit)));
        connect(delBtn, &QPushButton::clicked, this, [this, env]() { remove(env); });
        actions->addWidget(editBtn);
        actions->addWidget(delBtn);
        card->addLayout(actions);

        grid->addWidget(card, rowN, col, Qt::AlignTop);
        if (++col >= cols) { col = 0; ++rowN; }
    }
    root->addLayout(grid);
    root->addStretch();
}

void EnvironmentsTab::addOrEdit(const Row &existing) {
    EnvironmentDialog dlg(existing, this);
    if (dlg.exec() != QDialog::Accepted) return;
    if (dlg.editingId() >= 0)
        Db::updateRow("environments", dlg.editingId(), dlg.data());
    else
        Db::insertRow("environments", dlg.data());
    Toast::show(this, "Environment saved.", Toast::Success);
    m_main->refreshChrome();
    refresh();
}

void EnvironmentsTab::remove(const Row &env) {
    const int id = M::i(env, "id");
    const int plantCount = Db::count("plants", "environment_id=?", {id});
    QMessageBox box(this);
    box.setWindowTitle("Delete Environment");
    box.setText(QString("Delete \"%1\"?").arg(M::s(env, "name")));
    box.setInformativeText(plantCount > 0
        ? QString("%1 plant(s) will be unlinked from this environment.").arg(plantCount)
        : "This cannot be undone.");
    box.setStandardButtons(QMessageBox::Yes | QMessageBox::No);
    box.setDefaultButton(QMessageBox::No);
    if (box.exec() != QMessageBox::Yes) return;

    // Unlink plants then delete.
    for (const Row &p : Db::getAll("plants", "environment_id=?", {id})) {
        Row upd; upd["environment_id"] = QVariant();
        Db::updateRow("plants", M::i(p, "id"), upd);
    }
    Db::deleteRow("environments", id);
    Toast::show(this, "Environment deleted.", Toast::Info);
    m_main->refreshChrome();
    refresh();
}
