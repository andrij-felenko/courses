class Worker : public QObject          // 1. звичайний QObject, НЕ нащадок QThread
{
    Q_OBJECT
public slots:
    void open()                        // 2. ресурс відкривається тут, уже в новій нитці
    {
        _dev = new QSerialPort(this);
        connect(_dev, &QIODevice::readyRead, this, [this] {
            emit dataReceived(_dev->readAll());   // 3. назовні йдуть ЛИШЕ байти
        });
        _dev->open(QIODevice::ReadWrite);
    }
    void write(const QByteArray &data) { if (_dev) _dev->write(data); }
    void close()                       { if (_dev) _dev->close(); }
signals:
    void dataReceived(const QByteArray &data);
private:
    QSerialPort *_dev = nullptr;
};

// власник живе в головній нитці
_thread = new QThread(this);
_worker = new Worker;                              // без батька — інакше не переселити
_worker->moveToThread(_thread);
connect(_thread, &QThread::started,  _worker, &Worker::open);
connect(_thread, &QThread::finished, _worker, &QObject::deleteLater);
connect(_worker, &Worker::dataReceived,
        this,    &Owner::_onData, Qt::QueuedConnection);   // 4. явно чергове
_thread->start();

// у бік пристрою — теж через чергу
QMetaObject::invokeMethod(_worker, "write", Qt::QueuedConnection,
                          Q_ARG(QByteArray, data));

// згортання: єдиний законний блокувальний перехід
QMetaObject::invokeMethod(_worker, "close", Qt::BlockingQueuedConnection);  // 5.
_thread->quit();
_thread->wait(3000);
