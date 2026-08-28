// CRC-8/SMBus: многочлен 0x07, старт 0x00, без відображення бітів.
// Класична побітова реалізація — компактна, не потребує таблиці (256 байтів).
// Для «123456789» дає 0xF4 — стандартне контрольне значення цього CRC.
static uint8_t crc8(const uint8_t *data, uint16_t len) {
    uint8_t crc = 0x00;
    for (uint16_t i = 0; i < len; i++) {
        crc ^= data[i];
        for (uint8_t b = 0; b < 8; b++)
            crc = (crc & 0x80) ? (uint8_t)((crc << 1) ^ 0x07) : (uint8_t)(crc << 1);
    }
    return crc;
}
