#pragma once

#include <QFrame>

class QLabel;

// Transient toast notification anchored to a window's bottom-right.
// Ports the success/error/warning/info toasts from helpers.py.
class Toast : public QFrame {
    Q_OBJECT
public:
    enum Level { Success, Error, Warning, Info };

    static void show(QWidget *anchor, const QString &message, Level level = Info,
                     int ms = 3200);

private:
    explicit Toast(QWidget *parent, const QString &message, Level level);
    void reposition();
    QWidget *m_anchorTop = nullptr;
};
