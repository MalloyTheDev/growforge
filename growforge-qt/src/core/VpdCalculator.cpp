#include "core/VpdCalculator.h"
#include <cmath>

namespace Vpd {

double calc(double tempC, double rh, double leafOffset) {
    const double leafTemp = tempC - leafOffset;
    const double svpAir  = 0.6108 * std::exp((17.27 * tempC)    / (tempC + 237.3));
    const double svpLeaf = 0.6108 * std::exp((17.27 * leafTemp) / (leafTemp + 237.3));
    const double avp = svpAir * (rh / 100.0);
    double vpd = svpLeaf - avp;
    if (vpd < 0) vpd = 0;
    return std::round(vpd * 100.0) / 100.0;
}

QString zone(double v) {
    if (v < 0.4) return "Danger (too low) — mold risk, slow transpiration";
    if (v < 0.8) return "Seedling / Early Veg — good for clones & seedlings";
    if (v < 1.0) return "Late Veg — ideal vegetative growth";
    if (v < 1.2) return "Early Flower — good transition";
    if (v < 1.4) return "Mid Flower — peak flowering";
    if (v < 1.6) return "Late Flower — ripening, low mold risk";
    return "Danger (too high) — plant stress, stomata close";
}

QString color(double v) {
    if (v < 0.4) return "#29b6f6";
    if (v < 0.8) return "#66bb6a";
    if (v < 1.0) return "#4caf50";
    if (v < 1.2) return "#8bc34a";
    if (v < 1.4) return "#ffc107";
    if (v < 1.6) return "#ff9800";
    return "#f44336";
}

double cToF(double c) { return std::round((c * 9.0 / 5.0 + 32.0) * 10.0) / 10.0; }
double fToC(double f) { return std::round((f - 32.0) * 5.0 / 9.0 * 10.0) / 10.0; }

} // namespace Vpd
