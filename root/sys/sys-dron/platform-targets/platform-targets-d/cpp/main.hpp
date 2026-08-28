namespace AndroidSerial {
    constexpr const char *kJniUsbSerialManagerClassName =
        "org/mavlink/qgroundcontrol/QGCUsbSerialManager";

    QList<QSerialPortInfo> availableDevices();
    int  open(const QString &portName, QSerialPortPrivate *classPtr);
    QByteArray read(int deviceId, int length, int timeout);
    int  write(int deviceId, const char *data, int length, int timeout, bool async);
    bool setParameters(int deviceId, int baudRate, int dataBits, int stopBits, int parity);
}
