#include "ui/pages/JournalTab.h"
#include "ui/MainWindow.h"
#include "ui/Toast.h"
#include "ui/widgets/CommonWidgets.h"
#include "ui/widgets/Icons.h"
#include "ui/dialogs/EventDialog.h"
#include "app/Config.h"
#include "app/Theme.h"
#include "data/Database.h"

#include <QPushButton>
#include <QComboBox>
#include <QHBoxLayout>
#include <QVBoxLayout>
#include <QLabel>

static Tone::T typeTone(const QString &t) {
    if (t == "Watering") return Tone::Cool;
    if (t.startsWith("Feeding") || t.startsWith("Training") || t == "Pruning") return Tone::Ok;
    if (t == "Photo") return Tone::Violet;
    if (t == "Issue Detected" || t == "Pest Treatment") return Tone::Warn;
    if (t == "Stage Change" || t == "Harvest") return Tone::Accent;
    return Tone::Muted;
}

JournalTab::JournalTab(MainWindow *main) : ScrollPage(main) {}

QWidget *JournalTab::eventRow(const Row &e, bool showPlant) {
    auto *w = new QWidget;
    auto *v = new QVBoxLayout(w);
    v->setContentsMargins(0, 6, 0, 6);
    v->setSpacing(3);

    auto *top = new QHBoxLayout;
    top->setSpacing(8);
    auto *date = new QLabel(M::s(e, "event_date").left(10));
    date->setStyleSheet(QString("color:%1; font-family:'%2'; font-size:11px;")
                            .arg(Theme::current().fg3, Theme::monoFamily()));
    top->addWidget(date);
    top->addWidget(makeBadge(M::s(e, "event_type"), typeTone(M::s(e, "event_type"))));
    if (showPlant && !M::s(e, "plant_name").isEmpty()) {
        auto *pn = new QLabel(M::s(e, "plant_name"));
        pn->setStyleSheet(QString("color:%1; font-size:12px;").arg(Theme::current().fg1));
        top->addWidget(pn);
    }
    top->addStretch();
    v->addLayout(top);

    const QString title = M::s(e, "title");
    const QString notes = M::s(e, "notes");
    if (!title.isEmpty() && title != M::s(e, "event_type")) {
        auto *t = new QLabel(title);
        t->setStyleSheet(QString("color:%1; font-weight:600;").arg(Theme::current().fg0));
        v->addWidget(t);
    }
    if (!notes.isEmpty()) {
        auto *n = new QLabel(notes);
        n->setWordWrap(true);
        n->setStyleSheet(QString("color:%1; font-size:12px;").arg(Theme::current().fg1));
        v->addWidget(n);
    }

    // Readings line
    QStringList parts;
    auto add = [&](const QString &lab, const QString &key, const QString &unit) {
        if (!M::s(e, key).isEmpty() && M::s(e, key) != "")
            parts << QString("%1 %2%3").arg(lab, M::s(e, key), unit);
    };
    add("pH", "ph", ""); add("EC", "ec", ""); add("PPM", "ppm", "");
    add("Temp", "temp", "°C"); add("RH", "humidity", "%");
    add("VPD", "vpd", "kPa"); add("Water", "water_ml", "ml");
    if (!parts.isEmpty()) {
        auto *r = new QLabel(parts.join("   ·   "));
        r->setStyleSheet(QString("color:%1; font-family:'%2'; font-size:11px;")
                             .arg(Theme::current().fg2, Theme::monoFamily()));
        v->addWidget(r);
    }
    return w;
}

void JournalTab::refresh() {
    auto *root = resetContent();

    // Header + filters
    auto *plantCombo = new QComboBox;
    plantCombo->addItem("All plants", -1);
    const Rows plants = Db::getAll("plants", "is_active=1", {}, "name ASC");
    for (const Row &p : plants) plantCombo->addItem(M::s(p, "name"), M::i(p, "id"));
    { int idx = plantCombo->findData(m_plantFilter); plantCombo->setCurrentIndex(idx >= 0 ? idx : 0); }

    auto *typeCombo = new QComboBox;
    typeCombo->addItem("All types", "");
    for (const QString &t : Config::EVENT_TYPES) typeCombo->addItem(t, t);
    { int idx = typeCombo->findData(m_typeFilter); typeCombo->setCurrentIndex(idx >= 0 ? idx : 0); }

    auto *logBtn = new QPushButton("  Log Event");
    logBtn->setProperty("variant", "primary");
    logBtn->setIcon(Icons::icon("plus", 14, QColor("#07110b")));
    logBtn->setEnabled(m_plantFilter >= 0);
    logBtn->setToolTip(m_plantFilter >= 0 ? "" : "Select a plant first");
    connect(logBtn, &QPushButton::clicked, this, [this, plants]() {
        QString name;
        for (const Row &p : plants) if (M::i(p, "id") == m_plantFilter) name = M::s(p, "name");
        EventDialog dlg(m_plantFilter, name, "Observation", this);
        if (dlg.exec() == QDialog::Accepted) {
            Db::insertRow("events", dlg.data());
            Toast::show(this, "Event logged.", Toast::Success);
            refresh();
        }
    });

    auto *filterRow = new QWidget;
    auto *fr = new QHBoxLayout(filterRow);
    fr->setContentsMargins(0, 0, 0, 0);
    fr->setSpacing(8);
    fr->addWidget(plantCombo);
    fr->addWidget(typeCombo);
    fr->addStretch();
    fr->addWidget(logBtn);

    root->addWidget(makePageHeader("Grow Journal",
        "Every logged event across your plants — filter by plant or type."));
    root->addWidget(filterRow);

    connect(plantCombo, &QComboBox::currentIndexChanged, this, [this, plantCombo](int) {
        m_plantFilter = plantCombo->currentData().toInt(); refresh();
    });
    connect(typeCombo, &QComboBox::currentIndexChanged, this, [this, typeCombo](int) {
        m_typeFilter = typeCombo->currentData().toString(); refresh();
    });

    // Query events
    Rows events = (m_plantFilter >= 0)
        ? Db::getPlantEvents(m_plantFilter, 500)
        : Db::getRecentEvents(500);
    if (!m_typeFilter.isEmpty()) {
        Rows filtered;
        for (const Row &e : events) if (M::s(e, "event_type") == m_typeFilter) filtered << e;
        events = filtered;
    }

    auto *card = new Card();
    if (events.isEmpty()) {
        card->addWidget(makeMuted("No journal entries match these filters."));
    } else {
        int n = 0;
        for (const Row &e : events) {
            if (n) card->addWidget(hLine());
            card->addWidget(eventRow(e, m_plantFilter < 0));
            ++n;
        }
    }
    root->addWidget(card);
    root->addStretch();
}
