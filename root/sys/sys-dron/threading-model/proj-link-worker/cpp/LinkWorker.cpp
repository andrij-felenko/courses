// LinkWorker.cpp
#include "LinkWorker.h"
#include <QUdpSocket>
#include <QNetworkDatagram>
#include <QThread>

LinkWorker::LinkWorker(quint16 localPort, LinkStatsPtr stats, QObject *parent)
    : QObject(parent)
    , _localPort(localPort)
    , _stats(std::move(stats))
{
    // Жодного ресурсу: тут ми ще в головній нитці.
}

void LinkWorker::openSocket()
{
    Q_ASSERT(QThread::currentThread() == thread());   // уже своя нитка

    _socket = new QUdpSocket(this);
    connect(_socket, &QUdpSocket::readyRead, this, &LinkWorker::_onReadyRead);

    if (!_socket->bind(QHostAddress::AnyIPv4, _localPort,
                       QUdpSocket::ShareAddress | QUdpSocket::ReuseAddressHint)) {
        emit failed(_socket->errorString());
        return;
    }
    emit opened(_socket->localPort());
}

void LinkWorker::closeSocket()
{
    if (!_socket) return;
    _socket->close();
    delete _socket;
    _socket = nullptr;
}
