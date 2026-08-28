static void jniDeviceException(JNIEnv*, jobject, jlong token, jstring message)
{
    const QString exceptionMessage = QJniObject(message).toString();
    // …пошук за токеном, потім перехід у потік-власник…
    p->exceptionArrived(exceptionMessage);
}

void QSerialPortPrivate::exceptionArrived(const QString& ex)
{
    setError(QSerialPortErrorInfo(QSerialPort::UnknownError, ex));
}
