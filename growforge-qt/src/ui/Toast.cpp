#include "ui/Toast.h"
#include "ui/widgets/Icons.h"
#include "app/Theme.h"
#include "app/Config.h"

#include <QHBoxLayout>
#include <QLabel>
#include <QTimer>
#include <QPropertyAnimation>
#include <QGraphicsOpacityEffect>

void Toast::show(QWidget *anchor, const QString &message, Level level, int ms) {
    if (!anchor) return;
    auto *t = new Toast(anchor->window(), message, level);
    t->QWidget::show();
    t->raise();
    QTimer::singleShot(ms, t, [t]() {
        auto *fx = new QGraphicsOpacityEffect(t);
        t->setGraphicsEffect(fx);
        auto *anim = new QPropertyAnimation(fx, "opacity", t);
        anim->setDuration(280);
        anim->setStartValue(1.0);
        anim->setEndValue(0.0);
        QObject::connect(anim, &QPropertyAnimation::finished, t, &QObject::deleteLater);
        anim->start(QAbstractAnimation::DeleteWhenStopped);
    });
}

Toast::Toast(QWidget *parent, const QString &message, Level level)
    : QFrame(parent), m_anchorTop(parent) {
    const Config::Palette &p = Theme::current();
    QString accent;
    QString iconName;
    switch (level) {
    case Success: accent = p.accent; iconName = "check";   break;
    case Error:   accent = p.crit;   iconName = "warning"; break;
    case Warning: accent = p.warn;   iconName = "warning"; break;
    case Info:
    default:      accent = p.sensor; iconName = "bell";    break;
    }

    setStyleSheet(QString(
        "QFrame { background:%1; border:1px solid %2; border-left:3px solid %3;"
        " border-radius:8px; }").arg(p.bg2, p.lineStrong, accent));

    auto *row = new QHBoxLayout(this);
    row->setContentsMargins(12, 10, 14, 10);
    row->setSpacing(10);

    auto *ico = new QLabel;
    ico->setPixmap(Icons::pixmap(iconName, 16, QColor(accent)));
    row->addWidget(ico, 0, Qt::AlignTop);

    auto *msg = new QLabel(message);
    msg->setWordWrap(true);
    msg->setStyleSheet(QString("color:%1; font-size:12.5px;").arg(p.fg0));
    msg->setMaximumWidth(320);
    row->addWidget(msg);

    setMinimumWidth(260);
    setMaximumWidth(380);
    adjustSize();
    reposition();
}

void Toast::reposition() {
    if (!m_anchorTop) return;
    const int margin = 18;
    QSize s = sizeHint();
    int x = m_anchorTop->width() - s.width() - margin;
    int y = m_anchorTop->height() - s.height() - margin;
    move(qMax(margin, x), qMax(margin, y));
}
