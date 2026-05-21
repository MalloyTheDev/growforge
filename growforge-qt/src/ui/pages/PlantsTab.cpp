#include "ui/pages/PlantsTab.h"
#include "ui/MainWindow.h"
#include "ui/Toast.h"
#include "ui/widgets/CommonWidgets.h"
#include "ui/widgets/Icons.h"
#include "ui/dialogs/PlantDialog.h"
#include "ui/dialogs/EventDialog.h"
#include "app/Config.h"
#include "app/Theme.h"
#include "data/Database.h"
#include "core/ReminderEngine.h"
#include "core/Exporter.h"

#include <QPushButton>
#include <QHBoxLayout>
#include <QVBoxLayout>
#include <QGridLayout>
#include <QLabel>
#include <QMessageBox>
#include <QCoreApplication>
#include <QDateTime>

PlantsTab::PlantsTab(MainWindow *main) : ScrollPage(main) {}

void PlantsTab::refresh() {
    auto *root = resetContent();

    auto *addBtn = new QPushButton("  Add Plant");
    addBtn->setProperty("variant", "primary");
    addBtn->setIcon(Icons::icon("plus", 14, QColor("#07110b")));
    connect(addBtn, &QPushButton::clicked, this, [this]() { addOrEdit({}); });
    root->addWidget(makePageHeader("Plants",
        "Every plant in your grow — lifecycle, logs, and yields.", addBtn));

    const int room = m_main->currentRoomId();
    Rows plants = room >= 0
        ? Db::getAll("plants", "is_active=1 AND environment_id=?", {room}, "updated_at DESC")
        : Db::getActivePlants();

    if (plants.isEmpty()) {
        auto *empty = new Card();
        empty->addWidget(makeMuted(room >= 0
            ? "No active plants in this room."
            : "No plants yet. Add your first plant to start tracking."));
        root->addWidget(empty);
        root->addStretch();
        return;
    }

    auto *grid = new QGridLayout;
    grid->setSpacing(14);
    int col = 0, rowN = 0;
    const int cols = 2;
    for (const Row &p : plants) {
        grid->addWidget(plantCard(p), rowN, col, Qt::AlignTop);
        if (++col >= cols) { col = 0; ++rowN; }
    }
    root->addLayout(grid);
    root->addStretch();
}

QWidget *PlantsTab::plantCard(const Row &p) {
    auto *card = new Card(M::s(p, "name"));
    card->setHeaderRight(makeStageBadge(M::s(p, "stage")));

    auto *badges = new QHBoxLayout;
    badges->setSpacing(6);
    badges->addWidget(makeBadge(M::s(p, "plant_type"), Tone::Cool));
    if (M::b(p, "is_mother")) badges->addWidget(makeBadge("Mother", Tone::Violet));
    badges->addStretch();
    auto *day = new QLabel(QString("Day %1").arg(M::daysSince(M::s(p, "start_date"))));
    day->setStyleSheet(QString("color:%1; font-family:'%2'; font-size:11px;")
                           .arg(Theme::current().fg2, Theme::monoFamily()));
    badges->addWidget(day);
    card->addLayout(badges);

    card->addWidget(makeKeyValue("Strain", M::s(p, "strain_name", "—")));
    card->addWidget(makeKeyValue("Genetics", M::s(p, "genetics_type")));
    QString envName = "—";
    if (!M::s(p, "environment_id").isEmpty()) {
        const Row env = Db::getRow("environments", M::i(p, "environment_id"));
        if (!env.isEmpty()) envName = M::s(env, "name");
    }
    card->addWidget(makeKeyValue("Environment", envName));
    if (!M::s(p, "medium").isEmpty())
        card->addWidget(makeKeyValue("Medium", M::s(p, "medium")));
    if (M::d(p, "yield_grams") > 0)
        card->addWidget(makeKeyValue("Yield", QString::number(M::d(p, "yield_grams")) + " g"));

    card->addWidget(hLine());

    auto *actions = new QHBoxLayout;
    actions->setSpacing(6);
    auto *logBtn = new QPushButton("  Log");
    logBtn->setIcon(Icons::icon("journal", 13, QColor(Theme::current().fg1)));
    connect(logBtn, &QPushButton::clicked, this, [this, p]() { logEvent(p); });
    auto *advBtn = new QPushButton("  Advance");
    advBtn->setIcon(Icons::icon("chev", 13, QColor(Theme::current().fg1)));
    connect(advBtn, &QPushButton::clicked, this, [this, p]() { advanceStage(p); });
    auto *editBtn = new QPushButton;
    editBtn->setIcon(Icons::icon("edit", 14, QColor(Theme::current().fg1)));
    editBtn->setToolTip("Edit"); editBtn->setFixedWidth(34);
    connect(editBtn, &QPushButton::clicked, this, [this, p]() { addOrEdit(p); });
    auto *pdfBtn = new QPushButton;
    pdfBtn->setIcon(Icons::icon("export", 14, QColor(Theme::current().fg1)));
    pdfBtn->setToolTip("Export PDF report"); pdfBtn->setFixedWidth(34);
    connect(pdfBtn, &QPushButton::clicked, this, [this, p]() { exportReport(p); });
    auto *delBtn = new QPushButton;
    delBtn->setProperty("variant", "danger");
    delBtn->setIcon(Icons::icon("trash", 14, QColor(Theme::current().crit)));
    delBtn->setToolTip("Archive plant"); delBtn->setFixedWidth(34);
    connect(delBtn, &QPushButton::clicked, this, [this, p]() { remove(p); });

    actions->addWidget(logBtn);
    actions->addWidget(advBtn);
    actions->addStretch();
    actions->addWidget(editBtn);
    actions->addWidget(pdfBtn);
    actions->addWidget(delBtn);
    card->addLayout(actions);
    return card;
}

void PlantsTab::addOrEdit(const Row &existing) {
    PlantDialog dlg(existing, this);
    if (dlg.exec() != QDialog::Accepted) return;
    Row data = dlg.data();
    data["updated_at"] = QDateTime::currentDateTime().toString("yyyy-MM-dd HH:mm:ss");
    if (dlg.editingId() >= 0)
        Db::updateRow("plants", dlg.editingId(), data);
    else
        Db::insertRow("plants", data);
    Toast::show(this, "Plant saved.", Toast::Success);
    m_main->refreshChrome();
    refresh();
}

void PlantsTab::logEvent(const Row &plant) {
    EventDialog dlg(M::i(plant, "id"), M::s(plant, "name"), "Observation", this);
    if (dlg.exec() != QDialog::Accepted) return;
    Db::insertRow("events", dlg.data());
    Toast::show(this, "Event logged.", Toast::Success);
    refresh();
}

void PlantsTab::advanceStage(const Row &plant) {
    const QString cur = M::s(plant, "stage");
    const int idx = Config::STAGES.indexOf(cur);
    if (idx < 0 || idx >= Config::STAGES.size() - 1) {
        Toast::show(this, "Already at the final stage.", Toast::Warning);
        return;
    }
    const QString next = Config::STAGES.at(idx + 1);

    QMessageBox box(this);
    box.setWindowTitle("Advance Stage");
    box.setText(QString("Advance \"%1\" from %2 to %3?")
                    .arg(M::s(plant, "name"), cur, next));
    box.setStandardButtons(QMessageBox::Yes | QMessageBox::No);
    box.setDefaultButton(QMessageBox::Yes);
    if (box.exec() != QMessageBox::Yes) return;

    const int id = M::i(plant, "id");
    const QString today = QDate::currentDate().toString("yyyy-MM-dd");
    Row upd;
    upd["stage"] = next;
    upd["updated_at"] = QDateTime::currentDateTime().toString("yyyy-MM-dd HH:mm:ss");
    if (next == "Seedling")        upd["germ_date"] = today;
    else if (next == "Vegetative") upd["veg_date"] = today;
    else if (next == "Flowering")  upd["flower_date"] = today;
    else if (next == "Harvested")  upd["harvest_date"] = today;
    Db::updateRow("plants", id, upd);

    // Log a stage-change event + stage-appropriate reminders.
    Row ev;
    ev["plant_id"] = id;
    ev["event_type"] = "Stage Change";
    ev["event_date"] = QDateTime::currentDateTime().toString("yyyy-MM-dd HH:mm:ss");
    ev["title"] = "Advanced to " + next;
    ev["notes"] = QString("Stage advanced from %1 to %2.").arg(cur, next);
    Db::insertRow("events", ev);
    ReminderEngine::createDefaultReminders(id, M::s(plant, "name"), next);

    Toast::show(this, QString("Advanced to %1.").arg(next), Toast::Success);
    refresh();
}

void PlantsTab::remove(const Row &plant) {
    QMessageBox box(this);
    box.setWindowTitle("Archive Plant");
    box.setText(QString("Archive \"%1\"?").arg(M::s(plant, "name")));
    box.setInformativeText("It will be hidden but its journal history is kept.");
    box.setStandardButtons(QMessageBox::Yes | QMessageBox::No);
    box.setDefaultButton(QMessageBox::No);
    if (box.exec() != QMessageBox::Yes) return;
    Row upd; upd["is_active"] = 0;
    Db::updateRow("plants", M::i(plant, "id"), upd);
    Toast::show(this, "Plant archived.", Toast::Info);
    m_main->refreshChrome();
    refresh();
}

void PlantsTab::exportReport(const Row &plant) {
    const int id = M::i(plant, "id");
    const Rows events = Db::getPlantEvents(id, 500);
    Row env;
    if (!M::s(plant, "environment_id").isEmpty())
        env = Db::getRow("environments", M::i(plant, "environment_id"));
    const QString dir = QCoreApplication::applicationDirPath() + "/exports";
    const QString path = Exporter::exportPlantReportPdf(plant, events, env, dir);
    if (path.isEmpty())
        Toast::show(this, "PDF export failed.", Toast::Error);
    else
        Toast::show(this, "Report saved to exports/.", Toast::Success, 5000);
}
