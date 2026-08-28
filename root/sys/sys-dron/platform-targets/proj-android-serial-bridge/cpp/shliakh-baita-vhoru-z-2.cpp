void QSerialPortPrivate::newDataArrived(const char* bytes, int length)
{
    qint64 droppedBytes = 0;

    QMutexLocker locker(&_readMutex);
    int bytesToRead = length;
    if (readBufferMaxSize) {                       // переповнення відсікають ТУТ
        const qint64 totalBuffered = _pendingSizeLocked()
                                   + _bufferBytesEstimate.load(std::memory_order_relaxed);
        const qint64 headroom = readBufferMaxSize - totalBuffered;
        if (bytesToRead > headroom) {
            bytesToRead = static_cast<int>(qMax(qint64(0), headroom));
            droppedBytes = static_cast<qint64>(length - bytesToRead);
        }
    }

    if (bytesToRead > 0) {
        _pendingData.append(bytes, bytesToRead);
        _readWaitCondition.wakeAll();
    }
    locker.unlock();

    if (droppedBytes > 0) {
        qCWarning(AndroidSerialPortLog) << "Read buffer full, dropping" << droppedBytes << "bytes";
    }
    if (bytesToRead <= 0) {
        return;
    }

    _scheduleReadyRead();
}

void QSerialPortPrivate::_scheduleReadyRead()
{
    Q_Q(QSerialPort);
    if (!_readyReadPending.exchange(true)) {          // ← вся суть в одному рядку
        QPointer<QSerialPort> guard(q);
        QMetaObject::invokeMethod(q, [this, guard]() {
            if (!guard || !guard->isOpen()) { _readyReadPending.store(false); return; }
            QMutexLocker locker(&_readMutex);
            _drainPendingDataLocked();                 // злив у буфер QIODevice
            const bool more = (_pendingSizeLocked() > 0);
            _readyReadPending.store(false);
            locker.unlock();
            emit guard->readyRead();
            if (more) { _scheduleReadyRead(); }
        }, Qt::QueuedConnection);
    }
}
