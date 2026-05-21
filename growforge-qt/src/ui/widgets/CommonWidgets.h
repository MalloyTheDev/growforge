#pragma once

#include <QFrame>
#include <QString>
#include <QColor>

class QVBoxLayout;
class QHBoxLayout;
class QLabel;
class QWidget;
class QPushButton;
class Sparkline;

namespace Tone { enum T { Muted, Ok, Warn, Crit, Cool, Violet, Accent }; }

// Tone -> hex color (from the current theme palette).
QString toneColor(Tone::T t);
Tone::T stageTone(const QString &stage);

// ─── Factory helpers ─────────────────────────────────────────────────────────
QLabel  *makeTitle(const QString &text);
QLabel  *makeSub(const QString &text);
QLabel  *makeSectionTitle(const QString &text);
QLabel  *makeMuted(const QString &text);
QLabel  *makeBadge(const QString &text, Tone::T tone = Tone::Muted);
QLabel  *makeStageBadge(const QString &stage);
QFrame  *hLine();
QFrame  *vLine();

// A page header: big title + subtitle on the left, optional widget on the right.
QWidget *makePageHeader(const QString &title, const QString &subtitle,
                        QWidget *rightWidget = nullptr);

// A key/value row (muted key left, mono value right).
QWidget *makeKeyValue(const QString &key, const QString &value);

// ─── Card ────────────────────────────────────────────────────────────────────
// Rounded panel with optional header (title + right widget) and a body layout.
class Card : public QFrame {
    Q_OBJECT
public:
    explicit Card(const QString &title = QString(), QWidget *parent = nullptr);
    QVBoxLayout *body() const { return m_body; }
    void addWidget(QWidget *w);
    void addLayout(QLayout *l);
    void setHeaderRight(QWidget *w);

private:
    QVBoxLayout *m_body = nullptr;
    QHBoxLayout *m_head = nullptr;
};

// ─── MetricCard ──────────────────────────────────────────────────────────────
// Label + big mono value (+ unit) + optional sub line, styled as a Card.
class MetricCard : public QFrame {
    Q_OBJECT
public:
    MetricCard(const QString &label, const QString &value,
               const QString &unit = QString(), Tone::T tone = Tone::Accent,
               QWidget *parent = nullptr);
    void setValue(const QString &value);
    void setSub(const QString &sub);
    Sparkline *sparkline() const { return m_spark; }
    void enableSparkline(const QColor &color);

private:
    QLabel *m_value = nullptr;
    QLabel *m_sub = nullptr;
    Sparkline *m_spark = nullptr;
};
