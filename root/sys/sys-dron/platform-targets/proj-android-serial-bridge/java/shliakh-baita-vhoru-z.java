@Override
public void onNewData(final byte[] data) {
    if (data == null || data.length == 0) {
        return;
    }
    if (data.length <= MAX_NATIVE_CALLBACK_DATA_BYTES) {   // 16 КіБ
        emitDeviceNewData(classPtr, data);
        return;
    }
    int offset = 0;
    while (offset < data.length) {
        final int end = Math.min(offset + MAX_NATIVE_CALLBACK_DATA_BYTES, data.length);
        emitDeviceNewData(classPtr, Arrays.copyOfRange(data, offset, end));
        offset = end;
    }
}
