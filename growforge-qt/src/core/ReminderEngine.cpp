#include "core/ReminderEngine.h"
#include "data/Database.h"

#include <QTimer>
#include <QDateTime>

ReminderEngine::ReminderEngine(QObject *parent) : QObject(parent) {
    m_timer = new QTimer(this);
    connect(m_timer, &QTimer::timeout, this, &ReminderEngine::check);
}

void ReminderEngine::start(int intervalSeconds) {
    if (intervalSeconds < 5) intervalSeconds = 5;
    m_timer->start(intervalSeconds * 1000);
    QTimer::singleShot(1500, this, &ReminderEngine::check); // initial check shortly after launch
}

void ReminderEngine::stop() { m_timer->stop(); }

void ReminderEngine::check() {
    const Rows due = Db::getDueReminders();
    if (!due.isEmpty()) emit remindersDue(due);
}

int ReminderEngine::createReminder(int plantId, const QString &type, const QString &dueDate,
                                   const QString &message, bool recurring, int recurrenceDays) {
    Row r;
    if (plantId >= 0) r["plant_id"] = plantId;
    r["reminder_type"] = type;
    r["due_date"] = dueDate;
    r["message"] = message;
    r["is_recurring"] = recurring ? 1 : 0;
    r["recurrence_days"] = recurrenceDays;
    r["is_completed"] = 0;
    return Db::insertRow("reminders", r);
}

void ReminderEngine::completeReminder(int reminderId, bool reschedule) {
    const Row reminder = Db::getRow("reminders", reminderId);
    if (reminder.isEmpty()) return;

    Row upd;
    upd["is_completed"] = 1;
    upd["completed_at"] = QDateTime::currentDateTime().toString("yyyy-MM-dd HH:mm:ss");
    Db::updateRow("reminders", reminderId, upd);

    const int recurDays = M::i(reminder, "recurrence_days");
    if (reschedule && M::b(reminder, "is_recurring") && recurDays > 0) {
        const QString next = QDateTime::currentDateTime().addDays(recurDays)
                                 .toString("yyyy-MM-dd HH:mm:ss");
        createReminder(M::i(reminder, "plant_id", -1), M::s(reminder, "reminder_type"),
                       next, M::s(reminder, "message"), true, recurDays);
    }
}

void ReminderEngine::createDefaultReminders(int plantId, const QString &plantName,
                                            const QString &stage) {
    const QDateTime now = QDateTime::currentDateTime();
    auto due = [&](int days) { return now.addDays(days).toString("yyyy-MM-dd HH:mm:ss"); };

    if (stage == "Seedling" || stage == "Vegetative" || stage == "Flowering") {
        createReminder(plantId, "Watering", due(2), "Water " + plantName, true, 2);
        createReminder(plantId, "Feeding", due(4), "Feed " + plantName, true, 4);
    }
    if (stage == "Vegetative") {
        createReminder(plantId, "Check", due(7),
                       "Check " + plantName + " for sex / preflowers", false, 0);
    }
}
