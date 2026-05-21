#pragma once

#include <QWidget>

// VPD zone chart: temperature (x) vs RH (y) grid, each cell colored by its VPD
// zone, with a marker at the current (temp, RH). Mirrors the Growjs VpdChart.
class VpdChart : public QWidget {
    Q_OBJECT
public:
    explicit VpdChart(QWidget *parent = nullptr);
    void setMarker(double tempC, double rh);

protected:
    void paintEvent(QPaintEvent *) override;

private:
    double m_temp = 24.0;
    double m_rh = 55.0;
    static constexpr int kTminC = 18, kTmaxC = 32;   // x range
    static constexpr int kRhMin = 30, kRhMax = 90;   // y range
};
