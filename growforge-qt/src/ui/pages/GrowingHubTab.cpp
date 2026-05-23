#include "ui/pages/GrowingHubTab.h"
#include "ui/MainWindow.h"
#include "ui/widgets/CommonWidgets.h"
#include "app/Config.h"
#include "app/Theme.h"
#include "data/Database.h"
#include "data/KnowledgeBase.h"

#include <QTabWidget>
#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QLabel>
#include <QJsonObject>
#include <QJsonArray>

static QString rangeStr(const QJsonArray &a, const QString &unit) {
    if (a.size() < 2) return "—";
    return QString("%1–%2%3").arg(a[0].toDouble()).arg(a[1].toDouble()).arg(unit);
}

GrowingHubTab::GrowingHubTab(MainWindow *main) : ScrollPage(main) {}

QWidget *GrowingHubTab::buildGroup(const QString &groupKey, const QString &guideStage) {
    auto *page = new QWidget;
    auto *col = new QVBoxLayout(page);
    col->setContentsMargins(0, 14, 0, 0);
    col->setSpacing(14);

    // ── Guidance card ──
    const QJsonObject g = KB::stage(guideStage);
    auto *guide = new Card(guideStage + " — Targets & Guidance");

    auto *targets = new QHBoxLayout;
    auto addTarget = [&](const QString &label, const QString &val) {
        auto *box = new QVBoxLayout;
        auto *l = new QLabel(label.toUpper());
        l->setStyleSheet(QString("color:%1; font-family:'%2'; font-size:9px;")
                             .arg(Theme::current().fg3, Theme::monoFamily()));
        auto *v = new QLabel(val);
        v->setStyleSheet(QString("color:%1; font-family:'%2'; font-size:14px; font-weight:600;")
                             .arg(Theme::current().accent, Theme::monoFamily()));
        box->addWidget(l); box->addWidget(v);
        targets->addLayout(box);
    };
    addTarget("Temp", rangeStr(g.value("temp_range").toArray(), "°C"));
    addTarget("RH", rangeStr(g.value("rh_range").toArray(), "%"));
    addTarget("VPD", rangeStr(g.value("vpd_target").toArray(), " kPa"));
    addTarget("PPFD", rangeStr(g.value("ppfd").toArray(), ""));
    addTarget("Light", g.value("light_hours_photo").toString("—"));
    targets->addStretch();
    guide->addLayout(targets);

    if (!g.value("description").toString().isEmpty()) {
        guide->addWidget(hLine());
        guide->addWidget(makeMuted(g.value("description").toString()));
    }

    const QJsonArray checklist = g.value("checklist").toArray();
    if (!checklist.isEmpty()) {
        guide->addWidget(makeSectionTitle("Checklist"));
        for (const QJsonValue &c : checklist) {
            auto *item = new QLabel("•  " + c.toString());
            item->setWordWrap(true);
            item->setStyleSheet(QString("color:%1; font-size:12px;").arg(Theme::current().fg1));
            guide->addWidget(item);
        }
    }

    const QJsonArray issues = g.value("common_issues").toArray();
    if (!issues.isEmpty()) {
        guide->addWidget(makeSectionTitle("Common Issues"));
        for (const QJsonValue &iv : issues) {
            const QJsonArray pair = iv.toArray();
            if (pair.size() < 2) continue;
            auto *row = new QLabel(QString("<b>%1</b> — %2")
                .arg(pair[0].toString().toHtmlEscaped(), pair[1].toString().toHtmlEscaped()));
            row->setWordWrap(true);
            row->setStyleSheet(QString("color:%1; font-size:12px;").arg(Theme::current().fg1));
            guide->addWidget(row);
        }
    }
    col->addWidget(guide);

    // ── Plants in this group ──
    const QStringList stages = Config::STAGE_GROUPS.value(groupKey);
    QStringList ph; QVariantList params;
    for (const QString &s : stages) { ph << "?"; params << s; }
    const Rows plants = Db::getAll("plants",
        QString("is_active=1 AND stage IN (%1)").arg(ph.join(",")), params, "updated_at DESC");

    auto *plantsCard = new Card(QString("Plants (%1)").arg(plants.size()));
    if (plants.isEmpty()) {
        plantsCard->addWidget(makeMuted("No plants currently in this phase."));
    } else {
        int n = 0;
        for (const Row &p : plants) {
            if (n++) plantsCard->addWidget(hLine());
            auto *w = new QWidget;
            auto *r = new QHBoxLayout(w);
            r->setContentsMargins(0, 6, 0, 6);
            auto *name = new QLabel(M::s(p, "name"));
            name->setTextFormat(Qt::PlainText);
            name->setStyleSheet(QString("color:%1; font-weight:600;").arg(Theme::current().fg0));
            r->addWidget(name);
            auto *strain = new QLabel(M::s(p, "strain_name"));
            strain->setTextFormat(Qt::PlainText);
            strain->setStyleSheet(QString("color:%1; font-size:11px;").arg(Theme::current().fg2));
            r->addWidget(strain);
            r->addStretch();
            auto *day = new QLabel(QString("Day %1").arg(M::daysSince(M::s(p, "start_date"))));
            day->setStyleSheet(QString("color:%1; font-family:'%2'; font-size:11px;")
                                   .arg(Theme::current().fg2, Theme::monoFamily()));
            r->addWidget(day);
            r->addWidget(makeStageBadge(M::s(p, "stage")));
            plantsCard->addWidget(w);
        }
    }
    col->addWidget(plantsCard);
    col->addStretch();
    return page;
}

void GrowingHubTab::refresh() {
    auto *root = resetContent();
    root->addWidget(makePageHeader("Growing Hub",
        "Stage-by-stage guidance for plants in seed, veg, and flower."));

    auto *tabs = new QTabWidget;
    tabs->addTab(buildGroup("seed", "Seedling"), "Seed / Seedling");
    tabs->addTab(buildGroup("veg", "Vegetative"), "Vegetative");
    tabs->addTab(buildGroup("flower", "Flowering"), "Flowering");
    tabs->setCurrentIndex(m_tab);
    connect(tabs, &QTabWidget::currentChanged, this, [this](int i) { m_tab = i; });
    root->addWidget(tabs);
    root->addStretch();
}
