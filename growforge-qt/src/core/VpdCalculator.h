#pragma once

#include <QString>

// VPD (Vapor Pressure Deficit) — ports utils/vpd_calculator.py.
namespace Vpd {

// VPD in kPa via the Tetens formula (leaf offset default 2°C). Rounded to 2dp.
double calc(double tempC, double rh, double leafOffset = 2.0);

// Descriptive zone label and hex color for a VPD value.
QString zone(double vpd);
QString color(double vpd);

double cToF(double c);
double fToC(double f);

} // namespace Vpd
