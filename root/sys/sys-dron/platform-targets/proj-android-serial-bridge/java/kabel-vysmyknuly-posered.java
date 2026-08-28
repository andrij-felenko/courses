private static void handleUsbDeviceDetached(final Intent intent) {
    UsbDevice device = getUsbDevice(intent);
    if (device == null) {
        return;
    }
    for (final Integer resourceId : findResourceIdsForPhysicalDevice(device.getDeviceId())) {
        final UsbDeviceResources resources = deviceResourcesMap.get(resourceId);
        if (resources == null) {
            continue;
        }
        final long classPtr = resources.classPtr;   // ← знімають ДО close()
        close(resourceId);
        emitDeviceHasDisconnected(classPtr);
    }
}
