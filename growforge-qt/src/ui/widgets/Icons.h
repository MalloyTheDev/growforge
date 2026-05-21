#pragma once

#include <QString>
#include <QColor>
#include <QIcon>
#include <QPixmap>

class QPainter;
class QRectF;

// Minimal line-icon set drawn with QPainter (no external assets).
// Names mirror the Growjs icon set where practical.
namespace Icons {

void paint(QPainter *p, const QString &name, const QRectF &rect, const QColor &color,
           qreal stroke = 1.6);
QPixmap pixmap(const QString &name, int size, const QColor &color);
QIcon   icon(const QString &name, int size, const QColor &color);

} // namespace Icons
