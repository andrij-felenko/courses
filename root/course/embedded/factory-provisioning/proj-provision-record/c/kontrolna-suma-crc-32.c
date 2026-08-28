// CRC-32/ISO-HDLC (== IEEE 802.3 == zlib.crc32): відображений многочлен 0xEDB88320,
// старт 0xFFFFFFFF, фінальний XOR 0xFFFFFFFF. Побітова форма без таблиці на 1 КБ —
// на старті рахуємо суму раз, швидкодія тут не критична.
// Звіряльний вектор: crc32("123456789") == 0xCBF43926.
static uint32_t crc32_iso(const uint8_t *data, size_t len) {
    uint32_t crc = 0xFFFFFFFFu;
    for (size_t i = 0; i < len; i++) {
        crc ^= data[i];
        for (int b = 0; b < 8; b++)
            crc = (crc & 1u) ? (crc >> 1) ^ 0xEDB88320u : (crc >> 1);
    }
    return crc ^ 0xFFFFFFFFu;
}
