#pragma once

#include <QString>

class QLabel;

// Form validation helpers ported from helpers.py.
namespace Validate {

bool notEmpty(const QString &value);
bool date(const QString &value);            // enforces YYYY-MM-DD
bool positiveNumber(const QString &value, bool allowZero = false);

// Show/clear an inline error message on a (hidden-by-default) error label.
void showError(QLabel *errorLabel, const QString &message);
void clearError(QLabel *errorLabel);

} // namespace Validate
