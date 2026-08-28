private static void handleUsbPermission(final Intent intent) {
    UsbDevice device = getUsbDevice(intent);
    if (device == null) {
        return;
    }
    if (intent.getBooleanExtra(UsbManager.EXTRA_PERMISSION_GRANTED, false)) {
        addOrUpdateDevice(device);                       // дозволили — заводимо драйвер
    } else {
        for (final Integer resourceId : findResourceIdsForPhysicalDevice(device.getDeviceId())) {
            final UsbDeviceResources resources = deviceResourcesMap.get(resourceId);
            if (resources != null) {
                emitDeviceException(resources.classPtr, "USB Permission Denied");
            }
        }
    }
}
