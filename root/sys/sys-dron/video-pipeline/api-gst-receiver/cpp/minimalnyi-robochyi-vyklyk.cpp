auto *receiver = new GstVideoReceiver(this);

receiver->setUri(QStringLiteral("udp://0.0.0.0:5600"));
receiver->setRtpJitterLatencyMs(80);       // типове; 0 і lowLatency — крайності
receiver->setLowLatency(false);
receiver->setAutoReconnect(true);

// 1 · результат приходить сигналом, не поверненим значенням
connect(receiver, &VideoReceiver::onStartComplete, this,
        [this, receiver](VideoReceiver::STATUS status) {
    if (status != VideoReceiver::STATUS_OK) {
        qWarning() << "тракт не піднявся, код" << status;
        return;                            // при autoReconnect сторож спробує сам
    }
    receiver->startDecoding(_sinkHandle);  // стік уже створено й він живий
});

// 2 · показ увімкнено насправді — не за кодом, а за станом
connect(receiver, &VideoReceiver::decodingChanged, this, [](bool active) {
    qInfo() << (active ? "картинка йде" : "показ спинено");
});

connect(receiver, &VideoReceiver::recordingStarted, this, [](const QString &file) {
    qInfo() << "пишемо у" << file;
});

// 3 · виклик можна робити з будь-якої нитки
receiver->start(8);                        // 8 секунд тиші джерела = діагноз
