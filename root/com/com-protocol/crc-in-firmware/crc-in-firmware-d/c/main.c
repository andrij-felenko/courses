uint16_t crc16_ccitt(const uint8_t *data, size_t len) {
    uint16_t crc = 0xFFFF;                  // стартове значення регістра
    for (size_t i = 0; i < len; i++) {
        crc ^= (uint16_t)data[i] << 8;      // вливаємо байт у старші 8 бітів
        for (int b = 0; b < 8; b++)         // 8 тактів зсуву на байт
            crc = (crc & 0x8000) ? (crc << 1) ^ 0x1021
                                 : (crc << 1);
    }
    return crc;
}
