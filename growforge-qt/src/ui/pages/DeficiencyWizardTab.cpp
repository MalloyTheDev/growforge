#include "ui/pages/DeficiencyWizardTab.h"
#include "ui/widgets/CommonWidgets.h"
#include "app/Config.h"
#include "app/Theme.h"
#include "data/KnowledgeBase.h"

#include <QHBoxLayout>
#include <QVBoxLayout>
#include <QGridLayout>
#include <QFormLayout>
#include <QScrollArea>
#include <QLabel>
#include <QComboBox>
#include <QDoubleSpinBox>
#include <QPushButton>
#include <QJsonObject>
#include <QJsonArray>
#include <algorithm>

DeficiencyWizardTab::DeficiencyWizardTab(MainWindow *main) : Page(main) {
    auto *outer = new QVBoxLayout(this);
    outer->setContentsMargins(22, 22, 22, 22);
    outer->setSpacing(16);
    outer->addWidget(makePageHeader("Deficiency Wizard",
        "Select the symptoms you see and get a weighted diagnosis with fixes."));

    auto *cols = new QHBoxLayout;
    cols->setSpacing(14);

    // ── Inputs ──
    auto *inputCard = new Card("Symptoms");

    // Collect unique keywords from the symptom patterns.
    QStringList keywords;
    QSet<QString> seen;
    for (const QJsonValue &pv : KB::symptomPatterns()) {
        for (const QJsonValue &kv : pv.toObject().value("keywords").toArray()) {
            const QString k = kv.toString();
            if (!k.isEmpty() && !seen.contains(k)) { seen.insert(k); keywords << k; }
        }
    }
    keywords.sort();

    auto *kwGrid = new QGridLayout;
    kwGrid->setSpacing(6);
    int r = 0, c = 0;
    for (const QString &k : keywords) {
        auto *chip = makeChip(k);
        m_symptomChecks << chip;
        kwGrid->addWidget(chip, r, c);
        if (++c >= 3) { c = 0; ++r; }
    }
    inputCard->addLayout(kwGrid);
    inputCard->addWidget(hLine());

    auto *form = new QFormLayout;
    m_leaf = new QComboBox; m_leaf->addItem("Any location", ""); m_leaf->addItem("Older / lower", "older");
    m_leaf->addItem("Newer / upper", "newer");
    m_medium = new QComboBox; m_medium->addItem("Soil", "soil"); m_medium->addItem("Hydro / Coco", "hydro_coco");
    m_ph = new QDoubleSpinBox; m_ph->setRange(0, 14); m_ph->setValue(6.2); m_ph->setSingleStep(0.1);
    form->addRow("Affected leaves", m_leaf);
    form->addRow("Medium", m_medium);
    form->addRow("Root-zone pH", m_ph);
    inputCard->addLayout(form);

    auto *btn = new QPushButton("  Diagnose");
    btn->setProperty("variant", "primary");
    connect(btn, &QPushButton::clicked, this, &DeficiencyWizardTab::diagnose);
    inputCard->addWidget(btn);
    inputCard->body()->addStretch();

    // ── Results ──
    auto *resultScroll = new QScrollArea;
    resultScroll->setWidgetResizable(true);
    resultScroll->setFrameShape(QFrame::NoFrame);
    auto *resInner = new QWidget;
    m_results = new QVBoxLayout(resInner);
    m_results->setContentsMargins(0, 0, 0, 0);
    m_results->setSpacing(12);
    m_results->addWidget(makeMuted("Select symptoms and press Diagnose."));
    m_results->addStretch();
    resultScroll->setWidget(resInner);

    cols->addWidget(inputCard, 2);
    cols->addWidget(resultScroll, 3);
    outer->addLayout(cols, 1);
}

void DeficiencyWizardTab::diagnose() {
    // Clear results.
    QLayoutItem *item;
    while ((item = m_results->takeAt(0)) != nullptr) {
        if (item->widget()) item->widget()->deleteLater();
        delete item;
    }

    QSet<QString> selected;
    for (QPushButton *cb : m_symptomChecks) if (cb->isChecked()) selected.insert(cb->text());
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

        double score = pat.value("confidence").toDouble(0.5) * KB::ruleWeight(pat.value("rule_id").toString());
        // Multi-symptom bonus (cap +0.45).
        score += std::min(0.45, 0.15 * (matched - 1));
        // Leaf-location bonus.
        const QString patLeaf = pat.value("leaf_loc").toString();
        if (!leaf.isEmpty() && !patLeaf.isEmpty() && patLeaf == leaf) score += 0.10;
        // pH lockout context: nudge nutrient-lockout diagnoses up when pH is off.
        if (phOutOfRange) score += 0.05;

        results.append({pat.value("diagnosis").toString(), pat.value("fix").toString(),
                        std::min(1.0, score)});
    }

    std::sort(results.begin(), results.end(),
              [](const Result &a, const Result &b) { return a.score > b.score; });

    if (phOutOfRange) {
        auto *warn = new Card("pH Alert");
        warn->addWidget(makeMuted(QString(
            "Root-zone pH %1 is outside the optimal %2–%3 range for %4. "
            "Nutrient lockout is likely — correct pH before chasing a deficiency.")
            .arg(ph).arg(opt.size()==2?opt[0].toDouble():0).arg(opt.size()==2?opt[1].toDouble():0)
            .arg(m_medium->currentText())));
        m_results->addWidget(warn);
    }

    int shown = 0;
    for (const Result &res : results) {
        if (shown++ >= 6) break;
        const int pct = int(res.score * 100);
        Tone::T tone = pct >= 70 ? Tone::Crit : (pct >= 45 ? Tone::Warn : Tone::Muted);
        auto *card = new Card(res.diagnosis);
        card->setHeaderRight(makeBadge(QString("%1% match").arg(pct), tone));
        card->addWidget(makeMuted(res.fix));
        m_results->addWidget(card);
    }
    if (shown == 0)
        m_results->addWidget(makeMuted("No clear match. Try selecting more specific symptoms."));
    m_results->addStretch();
}
