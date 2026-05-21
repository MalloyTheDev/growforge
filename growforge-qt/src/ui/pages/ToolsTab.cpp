#include "ui/pages/ToolsTab.h"
#include "ui/widgets/CommonWidgets.h"
#include "ui/widgets/VpdChart.h"
#include "app/Theme.h"
#include "core/VpdCalculator.h"
#include "data/KnowledgeBase.h"

#include <QTabWidget>
#include <QScrollArea>
#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QFormLayout>
#include <QGridLayout>
#include <QLabel>
#include <QDoubleSpinBox>
#include <QSpinBox>
#include <QComboBox>
#include <QJsonObject>
#include <QJsonArray>

ToolsTab::ToolsTab(MainWindow *main) : Page(main) {
    auto *outer = new QVBoxLayout(this);
    outer->setContentsMargins(22, 22, 22, 22);
    outer->setSpacing(16);
    outer->addWidget(makePageHeader("Tools",
        "Calculators and references for dialing in your grow."));

    auto *tabs = new QTabWidget;
    tabs->addTab(buildVpd(), "VPD Calculator");
    tabs->addTab(buildYield(), "Yield Estimator");
    tabs->addTab(buildMixer(), "Nutrient Mixer");
    tabs->addTab(buildTraining(), "Training Library");
    outer->addWidget(tabs, 1);
}

QWidget *ToolsTab::buildVpd() {
    auto *w = new QWidget;
    auto *row = new QHBoxLayout(w);
    row->setContentsMargins(0, 14, 0, 0);
    row->setSpacing(14);

    auto *inputCard = new Card("Inputs");
    auto *form = new QFormLayout;
    auto *temp = new QDoubleSpinBox; temp->setRange(0, 50); temp->setValue(24); temp->setSuffix(" °C");
    auto *rh = new QDoubleSpinBox; rh->setRange(0, 100); rh->setValue(55); rh->setSuffix(" %");
    auto *leaf = new QDoubleSpinBox; leaf->setRange(0, 10); leaf->setValue(2); leaf->setSuffix(" °C");
    form->addRow("Air temp", temp);
    form->addRow("Humidity", rh);
    form->addRow("Leaf offset", leaf);
    inputCard->addLayout(form);

    auto *result = new QLabel;
    result->setStyleSheet(QString("font-family:'%1'; font-size:34px; font-weight:600;")
                              .arg(Theme::monoFamily()));
    auto *zone = new QLabel;
    zone->setWordWrap(true);
    inputCard->addWidget(hLine());
    inputCard->addWidget(makeSectionTitle("Result"));
    inputCard->addWidget(result);
    inputCard->addWidget(zone);
    inputCard->body()->addStretch();

    auto *chartCard = new Card("VPD Zone Chart");
    auto *chart = new VpdChart;
    chartCard->addWidget(chart);

    auto update = [=]() {
        const double v = Vpd::calc(temp->value(), rh->value(), leaf->value());
        const QString c = Vpd::color(v);
        result->setText(QString("%1 kPa").arg(v, 0, 'f', 2));
        result->setStyleSheet(QString("color:%1; font-family:'%2'; font-size:34px; font-weight:600;")
                                  .arg(c, Theme::monoFamily()));
        zone->setText(Vpd::zone(v));
        zone->setStyleSheet(QString("color:%1; font-size:12px;").arg(Theme::current().fg2));
        chart->setMarker(temp->value(), rh->value());
    };
    QObject::connect(temp, &QDoubleSpinBox::valueChanged, w, [update](double){ update(); });
    QObject::connect(rh, &QDoubleSpinBox::valueChanged, w, [update](double){ update(); });
    QObject::connect(leaf, &QDoubleSpinBox::valueChanged, w, [update](double){ update(); });
    update();

    row->addWidget(inputCard, 2);
    row->addWidget(chartCard, 3);
    return w;
}

QWidget *ToolsTab::buildYield() {
    auto *w = new QWidget;
    auto *col = new QVBoxLayout(w);
    col->setContentsMargins(0, 14, 0, 0);

    auto *card = new Card("Yield Estimator");
    auto *form = new QFormLayout;
    auto *watts = new QDoubleSpinBox; watts->setRange(0, 100000); watts->setValue(480); watts->setSuffix(" W");
    auto *plants = new QSpinBox; plants->setRange(1, 1000); plants->setValue(4);
    auto *exp = new QComboBox; exp->addItems({"Beginner", "Intermediate", "Advanced", "Expert"});
    exp->setCurrentIndex(1);
    form->addRow("Light wattage", watts);
    form->addRow("Plant count", plants);
    form->addRow("Experience", exp);
    card->addLayout(form);

    auto *out = new QLabel;
    card->addWidget(hLine());
    card->addWidget(makeSectionTitle("Estimated dry yield"));
    card->addWidget(out);

    auto update = [=]() {
        // grams per watt by experience (rough, illustrative).
        const double gpw[] = {0.5, 0.8, 1.0, 1.2};
        const double f = gpw[qBound(0, exp->currentIndex(), 3)];
        const double mid = watts->value() * f;
        out->setText(QString("%1 – %2 g  (≈ %3 g/plant)")
                         .arg(mid * 0.85, 0, 'f', 0).arg(mid * 1.15, 0, 'f', 0)
                         .arg(mid / plants->value(), 0, 'f', 0));
        out->setStyleSheet(QString("color:%1; font-family:'%2'; font-size:22px; font-weight:600;")
                               .arg(Theme::current().accent, Theme::monoFamily()));
    };
    QObject::connect(watts, &QDoubleSpinBox::valueChanged, w, [update](double){ update(); });
    QObject::connect(plants, &QSpinBox::valueChanged, w, [update](int){ update(); });
    QObject::connect(exp, &QComboBox::currentIndexChanged, w, [update](int){ update(); });
    update();
    card->body()->addStretch();

    col->addWidget(card);
    col->addStretch();
    return w;
}

QWidget *ToolsTab::buildMixer() {
    auto *w = new QWidget;
    auto *col = new QVBoxLayout(w);
    col->setContentsMargins(0, 14, 0, 0);

    auto *card = new Card("Nutrient Mixer");
    card->addWidget(makeMuted("Enter reservoir size and dose rates to get total amounts."));
    auto *form = new QFormLayout;
    auto *liters = new QDoubleSpinBox; liters->setRange(0, 10000); liters->setValue(10); liters->setSuffix(" L");
    auto *partA = new QDoubleSpinBox; partA->setRange(0, 100); partA->setValue(3); partA->setSuffix(" ml/L");
    auto *partB = new QDoubleSpinBox; partB->setRange(0, 100); partB->setValue(3); partB->setSuffix(" ml/L");
    auto *calmag = new QDoubleSpinBox; calmag->setRange(0, 100); calmag->setValue(1); calmag->setSuffix(" ml/L");
    form->addRow("Reservoir", liters);
    form->addRow("Part A", partA);
    form->addRow("Part B", partB);
    form->addRow("Cal-Mag", calmag);
    card->addLayout(form);
    card->addWidget(hLine());

    auto *out = new QLabel;
    out->setStyleSheet(QString("color:%1; font-family:'%2'; font-size:13px;")
                           .arg(Theme::current().fg0, Theme::monoFamily()));
    card->addWidget(out);
    auto update = [=]() {
        const double L = liters->value();
        out->setText(QString("Part A: %1 ml\nPart B: %2 ml\nCal-Mag: %3 ml")
                         .arg(partA->value() * L, 0, 'f', 1)
                         .arg(partB->value() * L, 0, 'f', 1)
                         .arg(calmag->value() * L, 0, 'f', 1));
    };
    for (QDoubleSpinBox *sb : {liters, partA, partB, calmag})
        QObject::connect(sb, &QDoubleSpinBox::valueChanged, w, [update](double){ update(); });
    update();
    card->body()->addStretch();

    col->addWidget(card);
    col->addStretch();
    return w;
}

QWidget *ToolsTab::buildTraining() {
    auto *scroll = new QScrollArea;
    scroll->setWidgetResizable(true);
    scroll->setFrameShape(QFrame::NoFrame);
    auto *inner = new QWidget;
    auto *col = new QVBoxLayout(inner);
    col->setContentsMargins(0, 14, 0, 0);
    col->setSpacing(14);

    const QJsonObject tech = KB::trainingTechniques();
    for (auto it = tech.constBegin(); it != tech.constEnd(); ++it) {
        const QJsonObject t = it.value().toObject();
        auto *card = new Card(it.key());

        auto *meta = new QHBoxLayout;
        meta->setSpacing(6);
        meta->addWidget(makeBadge(t.value("difficulty").toString("—"), Tone::Cool));
        meta->addWidget(makeBadge(t.value("stage").toString("—"), Tone::Muted));
        if (t.value("auto_safe").toBool())
            meta->addWidget(makeBadge("Auto-safe", Tone::Ok));
        meta->addWidget(makeBadge("+" + QString::number(t.value("yield_boost").toDouble()) + "% yield", Tone::Accent));
        meta->addStretch();
        card->addLayout(meta);

        if (!t.value("description").toString().isEmpty())
            card->addWidget(makeMuted(t.value("description").toString()));

        const QJsonArray steps = t.value("steps").toArray();
        if (!steps.isEmpty()) {
            card->addWidget(makeSectionTitle("Steps"));
            int i = 1;
            for (const QJsonValue &s : steps) {
                auto *l = new QLabel(QString("%1. %2").arg(i++).arg(s.toString()));
                l->setWordWrap(true);
                l->setStyleSheet(QString("color:%1; font-size:12px;").arg(Theme::current().fg1));
                card->addWidget(l);
            }
        }
        const QJsonArray cautions = t.value("cautions").toArray();
        if (!cautions.isEmpty()) {
            card->addWidget(makeSectionTitle("Cautions"));
            for (const QJsonValue &c : cautions) {
                auto *l = new QLabel("⚠  " + c.toString());
                l->setWordWrap(true);
                l->setStyleSheet(QString("color:%1; font-size:12px;").arg(Theme::current().warn));
                card->addWidget(l);
            }
        }
        col->addWidget(card);
    }
    col->addStretch();
    scroll->setWidget(inner);
    return scroll;
}
