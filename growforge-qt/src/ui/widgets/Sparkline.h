#pragma once

#include <QWidget>
#include <QVector>
#include <QColor>

// Lightweight sparkline / area mini-chart drawn with QPainter.
class Sparkline : public QWidget {
    Q_OBJECT
public:
    explicit Sparkline(QWidget *parent = nullptr);

    void setData(const QVector<double> &data);
    void setColor(const QColor &c);
    void setFill(bool on);
    void setRange(double lo, double hi);   // y-range; auto if not set

protected:
    void paintEvent(QPaintEvent *) override;

private:
    QVector<double> m_data;
    QColor m_color;
    bool m_fill = true;
    bool m_hasRange = false;
    double m_lo = 0, m_hi = 1;
};
