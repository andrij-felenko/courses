// CRC8/DVB-S2, поліном 0xD5. Рахуємо по байтах: тип + дані.
uint8_t crsf_crc8(const uint8_t *ptr, uint8_t len) {
    uint8_t crc = 0;
    for (uint8_t i = 0; i < len; ++i) {
        crc ^= ptr[i];                       // вкидаємо черговий байт
        for (uint8_t b = 0; b < 8; ++b)      // прокручуємо 8 бітів
            crc = (crc & 0x80) ? (crc << 1) ^ 0xD5 : (crc << 1);
    }
    return crc;
}

// Перевірка цілого кадру:
//   frame[0] = 0xC8 (старт), frame[1] = len, далі тип+дані, останній = CRC
bool crsf_frame_ok(const uint8_t *frame) {
    uint8_t len = frame[1];                  // тип + дані + CRC
    uint8_t got = frame[2 + len - 1];        // останній байт = присланий CRC
    uint8_t calc = crsf_crc8(&frame[2], len - 1); // від типу до кінця даних
    return got == calc;
}
