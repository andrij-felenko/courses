QGCSerialListener listener = new QGCSerialListener(classPtr);
SerialInputOutputManager ioManager = new SerialInputOutputManager(port, listener);

int readBufferSize = READ_BUF_SIZE;
final UsbEndpoint readEndpoint = port.getReadEndpoint();
if (readEndpoint != null) {
    readBufferSize = Math.max(readEndpoint.getMaxPacketSize(), READ_BUF_SIZE);
}
ioManager.setReadBufferSize(readBufferSize);

ioManager.setReadTimeout(0);
ioManager.setReadQueue(2);
ioManager.setWriteTimeout(0);
ioManager.setThreadPriority(Process.THREAD_PRIORITY_URGENT_AUDIO);
