int64_t TlogReader::resyncFrom(int64_t byteOffset) {
    if (!_f.seek(byteOffset)) return -1;

    // Обов'язково: у слоті каналу лежить недобудований кадр із попереднього місця
    // файлу, і без скидання перший же байт нової позиції продовжив би саме його.
    mavlink_reset_channel_status(kChannel);

    mavlink_message_t msg{};
    mavlink_status_t  st{};
    uint8_t b = 0;
    for (int64_t scanned = 0; scanned < kResyncLimit && _f.getByte(b); ++scanned) {
        if (!mavlink_parse_char(kChannel, b, &msg, &st)) continue;

        const int64_t frameEnd   = _f.tell();
        const int64_t frameStart = frameEnd - mavlink_msg_get_send_buffer_length(&msg);
        const int64_t recStart   = frameStart - kStampBytes;
        if (recStart >= 0) return recStart;
    }
    return -1;
}
