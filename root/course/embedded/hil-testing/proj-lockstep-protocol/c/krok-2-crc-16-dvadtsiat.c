// CRC-16/CCITT-FALSE: поліном 0x1021, початок 0xFFFF, без інверсії на виході.
// Побітно — повільно, але прозоро; для 40-байтового кадру цього з головою.
uint16_t crc16(const uint8_t *data, size_t n) {
    uint16_t crc = 0xFFFF;
    for (size_t i = 0; i < n; i++) {
        crc ^= (uint16_t)data[i] << 8;      // байт у старший розряд
        for (int b = 0; b < 8; b++) {
            if (crc & 0x8000)               // старший біт одиниця?
                crc = (crc << 1) ^ 0x1021;  // зсув і «ділення» на поліном
            else
                crc <<= 1;
        }
    }
    return crc;
}
