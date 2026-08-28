DemoLink::~DemoLink()
{
    // 1. Закрити ресурс і ДОЧЕКАТИСЯ: далі об'єкти вже гинуть.
    QMetaObject::invokeMethod(_worker, "closeSocket", Qt::BlockingQueuedConnection);

    // 2. Попросити цикл подій робітника вийти.
    _thread->quit();

    // 3. Дочекатися, поки нитка справді стане.
    if (!_thread->wait(kShutdownMs))
        qCritical("канал: робітник не зупинився за %d мс", kShutdownMs);

    // _worker знищить себе сам, у своїй нитці; _thread — як дитина цього об'єкта.
}
