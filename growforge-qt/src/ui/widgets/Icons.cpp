#include "ui/widgets/Icons.h"

#include <QPainter>
#include <QPainterPath>
#include <QRectF>
#include <cmath>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

namespace Icons {

// All glyphs are drawn in a 24x24 logical box, then scaled to `rect`.
static void drawGlyph(QPainter *p, const QString &n) {
    QPen pen(p->pen());
    auto line = [&](qreal x1, qreal y1, qreal x2, qreal y2) {
        p->drawLine(QPointF(x1, y1), QPointF(x2, y2));
    };
    auto rrect = [&](qreal x, qreal y, qreal w, qreal h, qreal r) {
        p->drawRoundedRect(QRectF(x, y, w, h), r, r);
    };
    auto circle = [&](qreal cx, qreal cy, qreal r) {
        p->drawEllipse(QPointF(cx, cy), r, r);
    };

    if (n == "dashboard") {
        rrect(3, 3, 7, 7, 1.5); rrect(14, 3, 7, 7, 1.5);
        rrect(3, 14, 7, 7, 1.5); rrect(14, 14, 7, 7, 1.5);
    } else if (n == "growing" || n == "sprout") {
        line(12, 21, 12, 11);
        QPainterPath l1; l1.moveTo(12, 13); l1.cubicTo(8, 13, 5, 10, 5, 6);
        l1.cubicTo(9, 6, 12, 9, 12, 13); p->drawPath(l1);
        QPainterPath l2; l2.moveTo(12, 12); l2.cubicTo(15, 12, 18, 9, 18, 6);
        l2.cubicTo(15, 6, 12, 9, 12, 12); p->drawPath(l2);
    } else if (n == "plants" || n == "leaf") {
        QPainterPath path; path.moveTo(5, 19);
        path.cubicTo(5, 9, 12, 5, 19, 5);
        path.cubicTo(19, 14, 13, 19, 5, 19);
        p->drawPath(path);
        line(8, 16, 16, 8);
    } else if (n == "env" || n == "thermo") {
        rrect(9.5, 3, 5, 12, 2.5);
        circle(12, 18, 3.2);
        line(12, 9, 12, 16);
    } else if (n == "journal" || n == "log" || n == "book") {
        rrect(5, 4, 14, 16, 2);
        line(9, 4, 9, 20);
        line(12, 9, 16, 9); line(12, 13, 16, 13);
    } else if (n == "calendar") {
        rrect(4, 5, 16, 15, 2);
        line(4, 9, 20, 9);
        line(8, 3, 8, 6); line(16, 3, 16, 6);
    } else if (n == "cloning" || n == "scissors") {
        circle(7, 7, 2.4); circle(7, 17, 2.4);
        line(9, 8.5, 19, 17); line(9, 15.5, 19, 7);
    } else if (n == "breeding" || n == "flask") {
        line(9, 3, 9, 9); line(15, 3, 15, 9);
        QPainterPath path; path.moveTo(9, 9); path.lineTo(5, 18);
        path.cubicTo(4.5, 20, 6, 21, 8, 21); path.lineTo(16, 21);
        path.cubicTo(18, 21, 19.5, 20, 19, 18); path.lineTo(15, 9);
        p->drawPath(path);
        line(7.5, 15, 16.5, 15);
    } else if (n == "deficiency" || n == "health") {
        QPainterPath path; path.moveTo(12, 20);
        path.cubicTo(4, 14, 4, 7, 8.5, 6);
        path.cubicTo(11, 5.5, 12, 8, 12, 8);
        path.cubicTo(12, 8, 13, 5.5, 15.5, 6);
        path.cubicTo(20, 7, 20, 14, 12, 20);
        p->drawPath(path);
    } else if (n == "tools" || n == "wrench") {
        QPainterPath path; path.moveTo(15, 5);
        path.cubicTo(18, 5, 20, 7, 19, 10);
        path.lineTo(13, 16); path.lineTo(8, 21);
        path.cubicTo(7, 22, 5, 20, 6, 19); path.lineTo(11, 14);
        path.lineTo(17, 8); path.cubicTo(15, 8, 14, 7, 15, 5);
        p->drawPath(path);
    } else if (n == "ai" || n == "chat") {
        QPainterPath path; path.moveTo(5, 16); path.lineTo(5, 7);
        path.cubicTo(5, 5.5, 6, 5, 7, 5); path.lineTo(17, 5);
        path.cubicTo(18, 5, 19, 5.5, 19, 7); path.lineTo(19, 13);
        path.cubicTo(19, 14.5, 18, 15, 17, 15); path.lineTo(9, 15);
        path.lineTo(5, 19); path.closeSubpath();
        p->drawPath(path);
        line(9, 10, 9, 10.1); line(12, 10, 12, 10.1); line(15, 10, 15, 10.1);
    } else if (n == "settings" || n == "gear") {
        circle(12, 12, 3);
        for (int i = 0; i < 8; ++i) {
            double a = i * M_PI / 4.0;
            line(12 + 5 * std::cos(a), 12 + 5 * std::sin(a),
                 12 + 7.5 * std::cos(a), 12 + 7.5 * std::sin(a));
        }
    } else if (n == "search") {
        circle(10.5, 10.5, 6); line(15, 15, 20, 20);
    } else if (n == "bell") {
        QPainterPath path; path.moveTo(7, 16);
        path.cubicTo(7, 10, 7, 6, 12, 6);
        path.cubicTo(17, 6, 17, 10, 17, 16); path.closeSubpath();
        p->drawPath(path);
        line(5, 16, 19, 16); circle(12, 19, 1.3);
    } else if (n == "plus") {
        line(12, 5, 12, 19); line(5, 12, 19, 12);
    } else if (n == "x" || n == "close") {
        line(6, 6, 18, 18); line(18, 6, 6, 18);
    } else if (n == "check") {
        line(5, 12, 10, 17); line(10, 17, 19, 6);
    } else if (n == "edit") {
        line(5, 19, 5, 15); line(5, 15, 15, 5); line(15, 5, 19, 9); line(19, 9, 9, 19); line(9, 19, 5, 19);
    } else if (n == "trash") {
        line(5, 7, 19, 7); rrect(7, 7, 10, 13, 1.5); line(9, 4, 15, 4);
        line(10, 10, 10, 17); line(14, 10, 14, 17);
    } else if (n == "drop" || n == "water") {
        QPainterPath path; path.moveTo(12, 4);
        path.cubicTo(18, 11, 18, 17, 12, 20);
        path.cubicTo(6, 17, 6, 11, 12, 4); p->drawPath(path);
    } else if (n == "warning") {
        QPainterPath path; path.moveTo(12, 4); path.lineTo(21, 20); path.lineTo(3, 20);
        path.closeSubpath(); p->drawPath(path);
        line(12, 10, 12, 15); line(12, 17.5, 12, 17.6);
    } else if (n == "user") {
        circle(12, 9, 3.4);
        QPainterPath path; path.moveTo(5.5, 20);
        path.cubicTo(6, 14, 18, 14, 18.5, 20); p->drawPath(path);
    } else if (n == "chevdown") {
        line(6, 9, 12, 15); line(12, 15, 18, 9);
    } else if (n == "chev" || n == "chevright") {
        line(9, 6, 15, 12); line(15, 12, 9, 18);
    } else if (n == "export" || n == "import") {
        line(12, 4, 12, 15);
        if (n == "export") { line(8, 8, 12, 4); line(12, 4, 16, 8); }
        else { line(8, 11, 12, 15); line(12, 15, 16, 11); }
        line(5, 19, 19, 19);
    } else if (n == "bulb") {
        circle(12, 9, 5); line(9, 18, 15, 18); line(10, 20, 14, 20);
    } else if (n == "trend") {
        line(4, 16, 10, 10); line(10, 10, 13, 13); line(13, 13, 20, 6);
        line(20, 6, 16, 6); line(20, 6, 20, 10);
    } else {
        circle(12, 12, 6); // fallback
    }
}

void paint(QPainter *p, const QString &name, const QRectF &rect, const QColor &color,
           qreal stroke) {
    p->save();
    p->setRenderHint(QPainter::Antialiasing, true);
    QPen pen(color);
    pen.setWidthF(stroke);
    pen.setCapStyle(Qt::RoundCap);
    pen.setJoinStyle(Qt::RoundJoin);
    p->setPen(pen);
    p->setBrush(Qt::NoBrush);
    p->translate(rect.topLeft());
    p->scale(rect.width() / 24.0, rect.height() / 24.0);
    drawGlyph(p, name);
    p->restore();
}

QPixmap pixmap(const QString &name, int size, const QColor &color) {
    qreal dpr = 2.0;
    QPixmap pm(int(size * dpr), int(size * dpr));
    pm.setDevicePixelRatio(dpr);
    pm.fill(Qt::transparent);
    QPainter pr(&pm);
    paint(&pr, name, QRectF(0, 0, size, size), color, 1.6);
    pr.end();
    return pm;
}

QIcon icon(const QString &name, int size, const QColor &color) {
    return QIcon(pixmap(name, size, color));
}

} // namespace Icons
