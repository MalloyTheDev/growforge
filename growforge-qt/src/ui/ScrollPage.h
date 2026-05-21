#pragma once

#include "ui/Page.h"
#include <QScrollArea>
#include <QVBoxLayout>
#include <QWidget>

// A Page with a vertical scroll area. resetContent() returns a fresh, padded
// content layout (discarding any previous content) for refresh()-style rebuilds.
class ScrollPage : public Page {
    Q_OBJECT
public:
    explicit ScrollPage(MainWindow *main, QWidget *parent = nullptr)
        : Page(main, parent) {
        auto *outer = new QVBoxLayout(this);
        outer->setContentsMargins(0, 0, 0, 0);
        outer->setSpacing(0);
        m_scroll = new QScrollArea;
        m_scroll->setObjectName("PageScroll");
        m_scroll->setWidgetResizable(true);
        m_scroll->setHorizontalScrollBarPolicy(Qt::ScrollBarAlwaysOff);
        outer->addWidget(m_scroll);
    }

protected:
    QVBoxLayout *resetContent(int margin = 22) {
        auto *w = new QWidget;
        auto *l = new QVBoxLayout(w);
        l->setContentsMargins(margin, margin, margin, margin);
        l->setSpacing(16);
        m_scroll->setWidget(w); // QScrollArea deletes the previous widget
        return l;
    }
    QScrollArea *m_scroll = nullptr;
};
