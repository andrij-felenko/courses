// DemoLink.h
#pragma once
#include "LinkTypes.h"
#include <QObject>

class LinkWorker;
class QThread;

class DemoLink : public QObject
{
    Q_OBJECT
public:
    explicit DemoLink(quint16 localPort, QObject *parent = nullptr);
    ~DemoLink() override;

    void send(const QByteArray &data);            // кликати з головної нитки
    LinkStats &stats() { return *_stats; }

signals:
    void bytesReceived(const QByteArray &data);

private:
    void _onChunk(const Chunk &chunk);

    LinkStatsPtr _stats = std::make_shared<LinkStats>();
    LinkWorker  *_worker = nullptr;
    QThread     *_thread = nullptr;
};
