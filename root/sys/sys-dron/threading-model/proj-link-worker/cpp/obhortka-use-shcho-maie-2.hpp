// DemoLink.cpp
#include "DemoLink.h"
#include "LinkWorker.h"
#include <QThread>

static constexpr int kShutdownMs = 2000;

DemoLink::DemoLink(quint16 localPort, QObject *parent)
    : QObject(parent)
    , _worker(new LinkWorker(localPort, _stats))   // БЕЗ батька — інакше не переселиться
    , _thread(new QThread(this))                   // сам об'єкт нитки живе тут
{
    qRegisterMetaType<Chunk>();

    _worker->moveToThread(_thread);

    connect(_thread, &QThread::started,  _worker, &LinkWorker::openSocket);
    connect(_thread, &QThread::finished, _worker, &QObject::deleteLater);

    connect(_worker, &LinkWorker::chunkReceived,
            this,    &DemoLink::_onChunk, Qt::QueuedConnection);

    _thread->start();
}
