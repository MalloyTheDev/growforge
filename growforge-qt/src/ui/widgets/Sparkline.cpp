#include "ui/widgets/Sparkline.h"
#include "app/Config.h"

#include <QPainter>
#include <QPainterPath>
#include <QLinearGradient>
#include <algorithm>

Sparkline::Sparkline(QWidget *parent) : QWidget(parent) {
    m_color = QColor(Config::DARK.accent);
    setMinimumHeight(28);
}

void Sparkline::setData(const QVector<double> &data) { m_data = data; update(); }
void Sparkline::setColor(const QColor &c) { m_color = c; update(); }
void Sparkline::setFill(bool on) { m_fill = on; update(); }
void Sparkline::setRange(double lo, double hi) { m_hasRange = true; m_lo = lo; m_hi = hi; update(); }

void Sparkline::paintEvent(QPaintEvent *) {
    if (m_data.size() < 2) return;
    QPainter p(this);
    p.setRenderHint(QPainter::Antialiasing, true);

    double lo = m_lo, hi = m_hi;
    if (!m_hasRange) {
        lo = *std::min_element(m_data.begin(), m_data.end());
        hi = *std::max_element(m_data.begin(), m_data.end());
    }
    if (hi - lo < 1e-9) hi = lo + 1.0;

    const double w = width();
    const double h = height();
    const double pad = 2.0;
    const double n = m_data.size() - 1;

    auto pt = [&](int i) -> QPointF {
        double x = pad + (w - 2 * pad) * (i / n);
        double norm = (m_data[i] - lo) / (hi - lo);
        double y = (h - pad) - (h - 2 * pad) * norm;
        return QPointF(x, y);
    };

    QPainterPath line;
    line.moveTo(pt(0));
    for (int i = 1; i < m_data.size(); ++i) line.lineTo(pt(i));

    if (m_fill) {
        QPainterPath area = line;
        area.lineTo(pt(m_data.size() - 1).x(), h - pad);
        area.lineTo(pt(0).x(), h - pad);
        area.closeSubpath();
        QLinearGradient g(0, 0, 0, h);
        QColor c0 = m_color; c0.setAlpha(70);
        QColor c1 = m_color; c1.setAlpha(0);
        g.setColorAt(0, c0); g.setColorAt(1, c1);
        p.fillPath(area, g);
    }

    QPen pen(m_color);
    pen.setWidthF(1.5);
    pen.setJoinStyle(Qt::RoundJoin);
    p.strokePath(line, pen);
}
