void LinkWorker::_onReadyRead()
{
    const qint64 stamp = monoNs();
    QByteArray burst;

    while (_socket->hasPendingDatagrams()) {
        const QNetworkDatagram dg = _socket->receiveDatagram();
        if (dg.data().isEmpty()) continue;

        _peerAddr = dg.senderAddress();
        _peerPort = dg.senderPort();

        if (burst.isEmpty())
            burst = dg.data();          // типовий випадок: одна датаграма, копії нема
        else
            burst.append(dg.data());

        _stats->datagrams.fetch_add(1, std::memory_order_relaxed);
    }
    if (burst.isEmpty()) return;

    _stats->bytesIn.fetch_add(burst.size(), std::memory_order_relaxed);
    _stats->emitted.fetch_add(1, std::memory_order_relaxed);
    emit chunkReceived(Chunk{ burst, stamp });
}
