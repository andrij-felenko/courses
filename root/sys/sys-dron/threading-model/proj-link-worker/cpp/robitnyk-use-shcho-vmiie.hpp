// LinkWorker.h
#pragma once
#include "LinkTypes.h"
#include <QObject>
#include <QHostAddress>

class QUdpSocket;

class LinkWorker : public QObject
{
    Q_OBJECT
public:
    LinkWorker(quint16 localPort, LinkStatsPtr stats, QObject *parent = nullptr);

public slots:
    void openSocket();                      // під'єднаний до сигналу «нитка почалася»
    void closeSocket();
    void writeData(const QByteArray &data);

signals:
    void chunkReceived(const Chunk &chunk);
    void opened(quint16 port);
    void failed(const QString &reason);

private slots:
    void _onReadyRead();

private:
    const quint16      _localPort;
    const LinkStatsPtr _stats;
    QUdpSocket        *_socket   = nullptr;
    QHostAddress       _peerAddr;
    quint16            _peerPort = 0;
};
