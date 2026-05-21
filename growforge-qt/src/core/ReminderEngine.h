#pragma once

#include "data/Models.h"
#include <QObject>
#include <QString>

class QTimer;

// Polls for due reminders on a QTimer (GUI thread — safe with Qt SQL).
// Ports utils/reminders.py (ReminderEngine + create_default_reminders).
class ReminderEngine : public QObject {
    Q_OBJECT
public:
    explicit ReminderEngine(QObject *parent = nullptr);

    void start(int intervalSeconds = 60);
    void stop();

    static int  createReminder(int plantId, const QString &type, const QString &dueDate,
                               const QString &message, bool recurring = false,
                               int recurrenceDays = 0);
    static void completeReminder(int reminderId, bool reschedule = true);

    // Stage-appropriate default reminders (watering/feeding/checks).
    static void createDefaultReminders(int plantId, const QString &plantName,
                                       const QString &stage);

signals:
    void remindersDue(const Rows &due);

private:
    void check();
    QTimer *m_timer = nullptr;
};
