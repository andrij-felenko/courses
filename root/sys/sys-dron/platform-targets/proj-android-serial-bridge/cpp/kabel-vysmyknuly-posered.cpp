template <typename Functor>
static bool dispatchToPortObject(QSerialPort* serialPort, Functor&& func, const char* context)
{
    QThread* const targetThread = serialPort->thread();
    if (targetThread == QThread::currentThread()) {
        std::forward<Functor>(func)();               // уже там, кличемо прямо
        return true;
    }
    if (targetThread && targetThread->eventDispatcher()) {
        // Блокувальний перехід: JNI-виклик не повернеться у Java,
        // доки порт справді не закрито в потоці-власнику.
        return QMetaObject::invokeMethod(serialPort, std::forward<Functor>(func),
                                         Qt::BlockingQueuedConnection);
    }
    std::forward<Functor>(func)();                   // потік без циклу подій — запасний шлях
    return true;
}
