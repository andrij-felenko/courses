/* Бітовий покроковий розрахунок CRC-16-CCITT */
uint16_t crc16_bitwise(uint16_t crc, uint8_t byte) {
    crc ^= (uint16_t)byte << 8;
    for (int i = 0; i < 8; ++i) {
        if (crc & 0x8000) {
            crc = (crc << 1) ^ 0x1021;
        } else {
            crc = crc << 1;
        }
    }
    return crc;
}
