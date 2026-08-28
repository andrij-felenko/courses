void LinkManager::shutdown()
{
    setConnectionsSuspended(tr("Shutdown"));   // 1. заборонити нові з'єднання
    disconnectAll();                           // 2. розірвати наявні

    // 3. дочекатися, поки зникнуть усі апарати
    while (MultiVehicleManager::instance()->vehicles()->count()) {
        QCoreApplication::processEvents(QEventLoop::ExcludeUserInputEvents);
    }
}
