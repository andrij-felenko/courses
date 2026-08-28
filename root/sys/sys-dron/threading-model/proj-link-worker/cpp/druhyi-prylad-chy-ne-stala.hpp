// LoopProbe.h — міряє головну нитку зсередини головної нитки
#pragma once
#include "LinkTypes.h"
#include <QObject>
#include <QAbstractEventDispatcher>
#include <algorithm>

class LoopProbe : public QObject
{
    Q_OBJECT
public:
    explicit LoopProbe(QObject *parent = nullptr) : QObject(parent)
    {
        auto *disp = QAbstractEventDispatcher::instance();   // диспетчер ЦІЄЇ нитки
        Q_ASSERT(disp);                        // існує лише після QCoreApplication
        connect(disp, &QAbstractEventDispatcher::awake,
                this, &LoopProbe::_onAwake);
        connect(disp, &QAbstractEventDispatcher::aboutToBlock,
                this, &LoopProbe::_onAboutToBlock);
    }

    qint64 longestBusyNs() const { return _maxBusyNs; }
    void   reset()               { _maxBusyNs = 0; }

private:
    void _onAwake() { _awakeNs = monoNs(); }

    void _onAboutToBlock()
    {
        if (_awakeNs == 0) return;
        _maxBusyNs = std::max(_maxBusyNs, monoNs() - _awakeNs);
        _awakeNs = 0;
    }

    qint64 _awakeNs   = 0;
    qint64 _maxBusyNs = 0;
};
