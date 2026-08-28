// Валідація та розпакування отриманого бінарного кадру (C99)
bool unpack_and_verify_frame(const uint8_t *buf, size_t len, telemetry_sample_t *out_sample) {
    if (len != sizeof(custom_frame_t) || buf[0] != 0xAA) {
        return false; // Неправильний розмір або магічний байт
    }
    
    custom_frame_t frame;
    memcpy(&frame, buf, sizeof(custom_frame_t));
    
    size_t payload_len = sizeof(custom_frame_t) - sizeof(uint16_t);
    uint16_t expected_crc = crc16_ccitt(buf, payload_len);
    
    if (frame.crc16 != expected_crc) {
        return false; // Пошкодження даних в ефірі
    }
    
    out_sample->timestamp_s  = frame.timestamp_s;
    out_sample->temp_centi_c = frame.temp_c;
    out_sample->humidity_pct = frame.hum_pct;
    out_sample->vbat_mv      = frame.vbat_mv;
    return true;
}
