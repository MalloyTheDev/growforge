#include "ui/Helpers.h"
#include "app/Theme.h"

#include <QLabel>
#include <QDate>
#include <QRegularExpression>

namespace Validate {

bool notEmpty(const QString &value) {
    return !value.trimmed().isEmpty();
}

bool date(const QString &value) {
    static const QRegularExpression re("^\\d{4}-\\d{2}-\\d{2}$");
    if (!re.match(value.trimmed()).hasMatch()) return false;
    return QDate::fromString(value.trimmed(), "yyyy-MM-dd").isValid();
}

bool positiveNumber(const QString &value, bool allowZero) {
    bool ok = false;
    double v = value.trimmed().toDouble(&ok);
    if (!ok) return false;
    return allowZero ? v >= 0.0 : v > 0.0;
}

void showError(QLabel *errorLabel, const QString &message) {
    if (!errorLabel) return;
    errorLabel->setText(message);
    errorLabel->setStyleSheet(QString("color:%1; font-size:11px;").arg(Theme::current().crit));
    errorLabel->setVisible(true);
}

void clearError(QLabel *errorLabel) {
    if (!errorLabel) return;
    errorLabel->clear();
    errorLabel->setVisible(false);
}

} // namespace Validate
