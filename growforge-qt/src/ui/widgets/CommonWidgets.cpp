#include "ui/widgets/CommonWidgets.h"
#include "ui/widgets/Sparkline.h"
#include "app/Theme.h"
#include "app/Config.h"

#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QLabel>
#include <QPushButton>

QString toneColor(Tone::T t) {
    const Config::Palette &p = Theme::current();
    switch (t) {
    case Tone::Ok:     return p.accent;
    case Tone::Warn:   return p.warn;
    case Tone::Crit:   return p.crit;
    case Tone::Cool:   return p.sensor;
    case Tone::Violet: return p.violet;
    case Tone::Accent: return p.accent;
    case Tone::Muted:
    default:           return p.fg2;
    }
}

Tone::T stageTone(const QString &stage) {
    if (stage == "Germination") return Tone::Violet;
    if (stage == "Seedling")    return Tone::Ok;
    if (stage == "Vegetative")  return Tone::Cool;
    if (stage == "Flowering")   return Tone::Warn;
    if (stage == "Flushing")    return Tone::Crit;
    if (stage == "Harvested")   return Tone::Ok;
    return Tone::Muted;
}

QLabel *makeTitle(const QString &text) {
    auto *l = new QLabel(text);
    l->setProperty("role", "title");
    l->setObjectName("PageTitle");
    return l;
}
QLabel *makeSub(const QString &text) {
    auto *l = new QLabel(text);
    l->setObjectName("PageSub");
    l->setProperty("role", "muted");
    l->setWordWrap(true);
    return l;
}
QLabel *makeSectionTitle(const QString &text) {
    auto *l = new QLabel(text.toUpper());
    l->setObjectName("SectionTitle");
    return l;
}
QLabel *makeMuted(const QString &text) {
    auto *l = new QLabel(text);
    l->setProperty("role", "muted");
    l->setWordWrap(true);
    return l;
}

QLabel *makeBadge(const QString &text, Tone::T tone) {
    auto *l = new QLabel(text);
    const QString c = toneColor(tone);
    QColor base(c);
    const QString bg = QString("rgba(%1,%2,%3,0.16)").arg(base.red()).arg(base.green()).arg(base.blue());
    const QString bd = QString("rgba(%1,%2,%3,0.42)").arg(base.red()).arg(base.green()).arg(base.blue());
    l->setStyleSheet(QString(
        "QLabel { color:%1; background:%2; border:1px solid %3; border-radius:999px;"
        " padding:1px 8px; font-family:'%4'; font-size:10.5px; }")
        .arg(c, bg, bd, Theme::monoFamily()));
    l->setAlignment(Qt::AlignCenter);
    l->setSizePolicy(QSizePolicy::Maximum, QSizePolicy::Maximum);
    return l;
}

QLabel *makeStageBadge(const QString &stage) {
    auto *l = makeBadge(stage, stageTone(stage));
    // Use the centralized stage color for the text/border tint.
    const QString c = Config::stageColor(stage);
    QColor base(c);
    const QString bg = QString("rgba(%1,%2,%3,0.16)").arg(base.red()).arg(base.green()).arg(base.blue());
    const QString bd = QString("rgba(%1,%2,%3,0.42)").arg(base.red()).arg(base.green()).arg(base.blue());
    l->setStyleSheet(QString(
        "QLabel { color:%1; background:%2; border:1px solid %3; border-radius:999px;"
        " padding:1px 8px; font-family:'%4'; font-size:10.5px; }")
        .arg(c, bg, bd, Theme::monoFamily()));
    return l;
}

QFrame *hLine() {
    auto *f = new QFrame;
    f->setFrameShape(QFrame::HLine);
    f->setFixedHeight(1);
    f->setStyleSheet(QString("background:%1; border:0;").arg(Theme::current().lineSoft));
    return f;
}
QFrame *vLine() {
    auto *f = new QFrame;
    f->setFrameShape(QFrame::VLine);
    f->setFixedWidth(1);
    f->setStyleSheet(QString("background:%1; border:0;").arg(Theme::current().lineSoft));
    return f;
}

QWidget *makePageHeader(const QString &title, const QString &subtitle, QWidget *rightWidget) {
    auto *w = new QWidget;
    auto *row = new QHBoxLayout(w);
    row->setContentsMargins(0, 0, 0, 0);
    auto *col = new QVBoxLayout;
    col->setSpacing(2);
    col->addWidget(makeTitle(title));
    if (!subtitle.isEmpty()) col->addWidget(makeSub(subtitle));
    row->addLayout(col);
    row->addStretch();
    if (rightWidget) row->addWidget(rightWidget, 0, Qt::AlignBottom);
    return w;
}

QWidget *makeKeyValue(const QString &key, const QString &value) {
    auto *w = new QWidget;
    auto *row = new QHBoxLayout(w);
    row->setContentsMargins(0, 4, 0, 4);
    auto *k = new QLabel(key);
    k->setProperty("role", "muted");
    auto *v = new QLabel(value);
    v->setProperty("mono", "true");
    v->setAlignment(Qt::AlignRight);
    row->addWidget(k);
    row->addStretch();
    row->addWidget(v);
    return w;
}

// ─── Card ────────────────────────────────────────────────────────────────────
Card::Card(const QString &title, QWidget *parent) : QFrame(parent) {
    setObjectName("Card");
    auto *outer = new QVBoxLayout(this);
    outer->setContentsMargins(0, 0, 0, 0);
    outer->setSpacing(0);

    if (!title.isEmpty()) {
        auto *head = new QWidget;
        head->setObjectName("CardHead");
        m_head = new QHBoxLayout(head);
        m_head->setContentsMargins(14, 12, 14, 12);
        auto *t = new QLabel(title.toUpper());
        t->setObjectName("CardTitle");
        m_head->addWidget(t);
        m_head->addStretch();
        outer->addWidget(head);
    }

    auto *bodyW = new QWidget;
    m_body = new QVBoxLayout(bodyW);
    m_body->setContentsMargins(14, 14, 14, 14);
    m_body->setSpacing(10);
    outer->addWidget(bodyW);
}
void Card::addWidget(QWidget *w) { m_body->addWidget(w); }
void Card::addLayout(QLayout *l) { m_body->addLayout(l); }
void Card::setHeaderRight(QWidget *w) {
    if (m_head) m_head->addWidget(w);
}

// ─── MetricCard ──────────────────────────────────────────────────────────────
MetricCard::MetricCard(const QString &label, const QString &value,
                       const QString &unit, Tone::T tone, QWidget *parent)
    : QFrame(parent) {
    setObjectName("Card");
    auto *col = new QVBoxLayout(this);
    col->setContentsMargins(14, 12, 14, 12);
    col->setSpacing(4);

    auto *lab = new QLabel(label.toUpper());
    lab->setObjectName("CardTitle");
    col->addWidget(lab);

    auto *valRow = new QHBoxLayout;
    valRow->setSpacing(4);
    m_value = new QLabel(value);
    m_value->setProperty("role", "metric");
    m_value->setStyleSheet(QString("color:%1; font-family:'%2'; font-size:28px; font-weight:600;")
                               .arg(toneColor(tone), Theme::monoFamily()));
    valRow->addWidget(m_value);
    if (!unit.isEmpty()) {
        auto *u = new QLabel(unit);
        u->setProperty("role", "muted");
        u->setProperty("mono", "true");
        u->setAlignment(Qt::AlignBottom);
        valRow->addWidget(u);
    }
    valRow->addStretch();
    col->addLayout(valRow);

    m_sub = new QLabel;
    m_sub->setProperty("role", "dim");
    m_sub->setStyleSheet(QString("color:%1; font-size:11px;").arg(Theme::current().fg3));
    m_sub->hide();
    col->addWidget(m_sub);
}
void MetricCard::setValue(const QString &value) { m_value->setText(value); }
void MetricCard::setSub(const QString &sub) {
    m_sub->setText(sub);
    m_sub->setVisible(!sub.isEmpty());
}
void MetricCard::enableSparkline(const QColor &color) {
    if (!m_spark) {
        m_spark = new Sparkline;
        m_spark->setColor(color);
        m_spark->setFixedHeight(30);
        static_cast<QVBoxLayout *>(layout())->addWidget(m_spark);
    }
}
