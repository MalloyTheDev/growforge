#include "ui/widgets/VpdChart.h"
#include "core/VpdCalculator.h"
#include "app/Theme.h"

#include <QPainter>

VpdChart::VpdChart(QWidget *parent) : QWidget(parent) {
    setMinimumHeight(240);
    setSizePolicy(QSizePolicy::Expanding, QSizePolicy::Expanding);
}

void VpdChart::setMarker(double tempC, double rh) {
    m_temp = tempC; m_rh = rh; update();
}

void VpdChart::paintEvent(QPaintEvent *) {
    QPainter p(this);
    p.setRenderHint(QPainter::Antialiasing, false);
    const Config::Palette &pal = Theme::current();

    const double left = 40, bottom = 24, top = 8, right = 8;
    const QRectF plot(left, top, width() - left - right, height() - top - bottom);
    if (plot.width() <= 0 || plot.height() <= 0) return;

    const int tSteps = kTmaxC - kTminC;     // columns
    const int rSteps = (kRhMax - kRhMin) / 5; // rows (5% each)
    const double cw = plot.width() / tSteps;
    const double ch = plot.height() / rSteps;

    // Cells: color by VPD zone. y axis: high RH at top.
    for (int xi = 0; xi < tSteps; ++xi) {
        for (int yi = 0; yi < rSteps; ++yi) {
            const double t = kTminC + xi + 0.5;
            const double rh = kRhMax - (yi + 0.5) * 5.0;
            const double vpd = Vpd::calc(t, rh);
            QColor c(Vpd::color(vpd));
            c.setAlpha(150);
            const QRectF cell(plot.left() + xi * cw, plot.top() + yi * ch, cw + 1, ch + 1);
            p.fillRect(cell, c);
        }
    }

    // Axis labels
    p.setPen(QColor(pal.fg3));
    QFont f(Theme::monoFamily(), 7);
    p.setFont(f);
    for (int t = kTminC; t <= kTmaxC; t += 2) {
        const double x = plot.left() + (t - kTminC) * cw;
        p.drawText(QRectF(x - 10, plot.bottom() + 2, 20, 16),
                   Qt::AlignCenter, QString::number(t));
    }
    for (int rh = kRhMin; rh <= kRhMax; rh += 10) {
        const double y = plot.top() + (kRhMax - rh) / 5.0 * ch;
        p.drawText(QRectF(0, y - 7, left - 6, 14),
                   Qt::AlignRight | Qt::AlignVCenter, QString::number(rh) + "%");
    }

    // Marker
    const double mt = qBound((double)kTminC, m_temp, (double)kTmaxC);
    const double mr = qBound((double)kRhMin, m_rh, (double)kRhMax);
    const double mx = plot.left() + (mt - kTminC) * cw;
    const double my = plot.top() + (kRhMax - mr) / 5.0 * ch;
    p.setRenderHint(QPainter::Antialiasing, true);
    p.setPen(QPen(QColor(pal.fg0), 2));
    p.setBrush(Qt::NoBrush);
    p.drawEllipse(QPointF(mx, my), 6, 6);
    p.drawLine(QPointF(mx - 10, my), QPointF(mx + 10, my));
    p.drawLine(QPointF(mx, my - 10), QPointF(mx, my + 10));
}
