#pragma once

#include <QString>
#include "app/Config.h"

class QApplication;

// Builds and applies the command-center QSS theme.
namespace Theme {

// Full application stylesheet derived from a palette.
QString buildStyleSheet(const Config::Palette &p);

// Apply theme ("dark" | "light") to the application: palette font + stylesheet.
void apply(QApplication *app, const QString &theme);

// Font families (with sensible Windows fallbacks for the Geist design fonts).
QString sansFamily();
QString monoFamily();

// The palette of the most recently applied theme (defaults to DARK).
const Config::Palette &current();
QString currentThemeName();

} // namespace Theme
