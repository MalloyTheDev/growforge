#include "ui/pages/DeficiencyWizardTab.h"
#include "ui/widgets/CommonWidgets.h"
#include "app/Config.h"
#include "app/Theme.h"
#include "data/KnowledgeBase.h"

#include <QHBoxLayout>
#include <QVBoxLayout>
#include <QFormLayout>
#include <QScrollArea>
#include <QLabel>
#include <QCheckBox>
#include <QComboBox>
#include <QDoubleSpinBox>
#include <QPushButton>
#include <QJsonObject>
#include <QJsonArray>
#include <QSet>
#include <algorithm>

// Curated, human-readable symptoms mapped to the keyword vocabulary used by the
// knowledge base's SYMPTOM_PATTERNS. Selecting a symptom contributes its keywords
// to the match set used by the weighted diagnosis.
namespace {
struct Symptom { const char *label; QStringList keywords; };
const QList<Symptom> kSymptoms = {
    {"Yellowing leaves",                 {"yellow", "yellowing"}},
    {"Pale / light-green leaves",        {"pale"}},
    {"Brown spots or spotting",          {"brown", "spots", "spotting", "speckled"}},
    {"Burnt or crispy tips / edges",     {"burnt", "crispy"}},
    {"Curling, clawing or taco-ing",     {"curl", "curling", "taco", "hook"}},
    {"Purple or red stems / petioles",   {"purple", "red"}},
    {"Dark green, overly lush leaves",   {"dark green", "very dark", "black green"}},
    {"Drooping, wilting or limp",        {"droop", "drooping", "wilt", "wilting", "limp"}},
    {"Twisted / deformed new growth",    {"twisted", "deformed", "distorted", "wrinkled", "cracked"}},
    {"Stunted, slow or stopped growth",  {"stunted", "slow", "stopped", "not growing"}},
    {"Stretchy / lanky / spindly",       {"stretching", "lanky", "spindly", "thin", "tall", "spire", "tower"}},
    {"Bleached / silver / bronze patches",{"bleached", "silver", "bronze", "albino", "gray", "grey"}},
    {"White powder on leaves",           {"powder", "powdery", "white"}},
    {"Webbing or tiny moving specks",    {"web", "webbing", "stippling", "dots"}},
    {"Fungus gnats / small flies",       {"gnat", "gnats", "fly", "flies"}},
    {"Sticky residue / honeydew",        {"sticky", "honeydew", "aphid", "aphids"}},
    {"Mushy, slimy, mold or rot",        {"mushy", "slimy", "rot", "mold", "fuzzy", "smell"}},
    {"Streaks or scarring on leaves",    {"streaks", "scarring", "bronze"}},
    {"Foxtailing / spires on buds",      {"foxtail", "foxtailing"}},
    {"Brittle / hollow stems",           {"brittle", "hollow"}},
};
} // namespace

DeficiencyWizardTab::DeficiencyWizardTab(MainWindow *main) : Page(main) {
    const Config::Palette &p = Theme::current();
    auto *outer = new QVBoxLayout(this);
    outer->setContentsMargins(22, 22, 22, 22);
    outer->setSpacing(16);
    outer->addWidget(makePageHeader("Deficiency Wizard",
        "Check the symptoms you see and get a weighted diagnosis with fixes."));

    auto *cols = new QHBoxLayout;
    cols->setSpacing(14);

    // ── Inputs ──
    auto *inputCard = new Card("Symptoms");

    // Scrollable, single-column checklist of readable symptoms.
    auto *symScroll = new QScrollArea;
    symScroll->setWidgetResizable(true);
    symScroll->setFrameShape(QFrame::NoFrame);
    symScroll->setHorizontalScrollBarPolicy(Qt::ScrollBarAlwaysOff);
    symScroll->setMinimumHeight(260);
    symScroll->setMaximumHeight(380);
    auto *symInner = new QWidget;
    auto *symList = new QVBoxLayout(symInner);
    symList->setContentsMargins(0, 0, 0, 0);
    symList->setSpacing(2);
    for (const Symptom &s : kSymptoms) {
        auto *cb = new QCheckBox(QString::fromUtf8(s.label));
        cb->setStyleSheet(QString("QCheckBox { color:%1; font-size:13px; padding:4px 2px; }")
                              .arg(p.fg0));
        m_symptomChecks << cb;
        symList->addWidget(cb);
    }
    symList->addStretch();
    symScroll->setWidget(symInner);
    inputCard->addWidget(symScroll);

    inputCard->addWidget(hLine());

    auto *form = new QFormLayout;
    m_leaf = new QComboBox;
    m_leaf->addItem("Any location", "");
    m_leaf->addItem("Older / lower leaves", "older");
    m_leaf->addItem("Newer / upper leaves", "newer");
    m_medium = new QComboBox;
    m_medium->addItem("Soil", "soil");
    m_medium->addItem("Hydro / Coco", "hydro_coco");
    m_ph = new QDoubleSpinBox;
    m_ph->setRange(0, 14); m_ph->setValue(6.2); m_ph->setSingleStep(0.1);
    form->addRow("Affected leaves", m_leaf);
    form->addRow("Medium", m_medium);
    form->addRow("Root-zone pH", m_ph);
    inputCard->addLayout(form);

    auto *btn = new QPushButton("  Diagnose");
    btn->setProperty("variant", "primary");
    connect(btn, &QPushButton::clicked, this, &DeficiencyWizardTab::diagnose);
    inputCard->addWidget(btn);

    // ── Results ──
    auto *resultScroll = new QScrollArea;
    resultScroll->setWidgetResizable(true);
    resultScroll->setFrameShape(QFrame::NoFrame);
    auto *resInner = new QWidget;
    m_results = new QVBoxLayout(resInner);
    m_results->setContentsMargins(0, 0, 0, 0);
    m_results->setSpacing(12);
    m_results->addWidget(makeMuted("Check the symptoms you see, then press Diagnose."));
    m_results->addStretch();
    resultScroll->setWidget(resInner);

    cols->addWidget(inputCard, 2);
    cols->addWidget(resultScroll, 3);
    outer->addLayout(cols, 1);
}

void DeficiencyWizardTab::clearResults() {
    QLayoutItem *item;
    while ((item = m_results->takeAt(0)) != nullptr) {
        if (item->widget()) item->widget()->deleteLater();
        delete item;
    }
}

void DeficiencyWizardTab::diagnose() {
    clearResults();

    // Build the keyword match-set from checked symptoms.
    QSet<QString> selected;
    for (int i = 0; i < m_symptomChecks.size() && i < kSymptoms.size(); ++i) {
        if (m_symptomChecks[i]->isChecked())
            for (const QString &k : kSymptoms[i].keywords) selected.insert(k);
    }
    const QString leaf = m_leaf->currentData().toString();
    const QString medium = m_medium->currentData().toString();
    const double ph = m_ph->value();

    if (selected.isEmpty()) {
        m_results->addWidget(makeMuted("Select at least one symptom."));
        m_results->addStretch();
        return;
    }

    // pH lockout context for the chosen medium.
    const QJsonObject lock = KB::phLockout().value(medium).toObject();
    const QJsonArray opt = lock.value("optimal_range").toArray();
    const bool phOutOfRange = opt.size() == 2 && (ph < opt[0].toDouble() || ph > opt[1].toDouble());

    struct Result { QString diagnosis, fix; double score; };
    QList<Result> results;
    for (const QJsonValue &pv : KB::symptomPatterns()) {
        const QJsonObject pat = pv.toObject();
        int matched = 0;
        for (const QJsonValue &kv : pat.value("keywords").toArray())
            if (selected.contains(kv.toString())) ++matched;
        if (matched == 0) continue;

        double score = pat.value("confidence").toDouble(0.5)
                       * KB::ruleWeight(pat.value("rule_id").toString());
        score += std::min(0.45, 0.15 * (matched - 1));
        const QString patLeaf = pat.value("leaf_loc").toString();
        if (!leaf.isEmpty() && !patLeaf.isEmpty() && patLeaf != "any") {
            if (patLeaf == leaf) score += 0.12;
            else score -= 0.12;     // wrong location lowers confidence
        }
        if (phOutOfRange) score += 0.05;
        results.append({pat.value("diagnosis").toString(), pat.value("fix").toString(),
                        std::clamp(score, 0.0, 1.0)});
    }

    std::sort(results.begin(), results.end(),
              [](const Result &a, const Result &b) { return a.score > b.score; });

    if (phOutOfRange) {
        auto *warn = new Card("pH Alert");
        warn->addWidget(makeMuted(QString(
            "Root-zone pH %1 is outside the optimal %2–%3 range for %4. Nutrient "
            "lockout is likely — correct pH before chasing a deficiency.")
            .arg(ph).arg(opt.size() == 2 ? opt[0].toDouble() : 0)
            .arg(opt.size() == 2 ? opt[1].toDouble() : 0)
            .arg(m_medium->currentText())));
        m_results->addWidget(warn);
    }

    int shown = 0;
    for (const Result &res : results) {
        if (res.score <= 0.0) continue;
        if (shown++ >= 6) break;
        const int pct = int(res.score * 100);
        const Tone::T tone = pct >= 70 ? Tone::Crit : (pct >= 45 ? Tone::Warn : Tone::Muted);
        auto *card = new Card(res.diagnosis);
        card->setHeaderRight(makeBadge(QString("%1% match").arg(pct), tone));
        card->addWidget(makeMuted(res.fix));
        m_results->addWidget(card);
    }
    if (shown == 0)
        m_results->addWidget(makeMuted("No clear match. Try selecting more specific symptoms "
                                       "or adjusting the affected-leaf location."));
    m_results->addStretch();
}
