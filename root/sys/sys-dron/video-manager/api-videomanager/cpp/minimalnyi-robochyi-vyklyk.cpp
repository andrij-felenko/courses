void MyTool::attach()
{
    VideoManager *vm = VideoManager::instance();
    VideoSettings *vs = SettingsManager::instance()->videoSettings();

    // Порівнюємо з константою, а не з тим, що показано користувачеві
    const QString source = vs->videoSource()->rawValue().toString();
    if (source == VideoSettings::videoSourceUDPH264) {
        qCDebug(MyLog) << "слухаємо" << QStringLiteral("udp://%1").arg(vs->udpUrl()->rawValue().toString());
    }

    // Ім'я файлу відоме лише тоді, коли приймач уже відкрив його
    connect(vm, &VideoManager::recordingStarted, this, [](const QString &filename) {
        qCDebug(MyLog) << "запис пішов у" << filename;
    });

    // Стеля сховища діє лише при ввімкненому прапорці — перевіряємо обидва факти
    if (vs->enableStorageLimit()->rawValue().toBool()) {
        qCDebug(MyLog) << "стеля" << vs->maxVideoSize()->rawValue().toUInt() << "МБ";
    }
}
