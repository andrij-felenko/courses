private static boolean openDriver(final UsbSerialPort port, final UsbDevice device,
                                  final int deviceId, final long classPtr) {
    if (port.isOpen()) {
        return true;
    }

    UsbDeviceConnection connection = usbManager.openDevice(device);
    if (connection == null) {
        QGCLogger.w(TAG, "No Usb Device Connection");
        emitDeviceException(classPtr, "No USB device connection for device: " + device.getDeviceName());
        return false;
    }

    try {
        port.open(connection);
    } catch (final IOException ex) {
        emitDeviceException(classPtr, "Error opening driver: " + ex.getMessage());
        connection.close();
        return false;
    }

    UsbDeviceResources resources = deviceResourcesMap.get(deviceId);
    if (resources != null) {
        resources.fileDescriptor = connection.getFileDescriptor();
    }
    return true;
}
