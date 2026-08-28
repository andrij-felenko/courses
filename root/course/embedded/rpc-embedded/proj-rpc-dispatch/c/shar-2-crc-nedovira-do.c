// CRC-16/CCITT (poly 0x1021, init 0xFFFF), побітово.
// len байтів за вказівником data → 16-бітна сума.
static uint16_t crc16(const uint8_t *data, size_t len) {
    uint16_t crc = 0xFFFFu;
    for (size_t i = 0; i < len; i++) {
        crc ^= (uint16_t)data[i] << 8;          // байт у старші 8 біт
        for (int b = 0; b < 8; b++) {
            if (crc & 0x8000u)                   // старший біт = 1?
                crc = (crc << 1) ^ 0x1021u;      // зсув + XOR з многочленом
            else
                crc = crc << 1;                  // просто зсув
        }
    }
    return crc;
}
