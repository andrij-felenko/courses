static const uint8_t crc8_table[256] = {
    0x00, 0x31, 0x62, 0x53, 0xC4, 0xF5, 0xA6, 0x97,
    0xB9, 0x88, 0xDB, 0xEA, 0x7D, 0x4C, 0x1F, 0x2E,
    /* ... 256 попередньо розрахованих байтів ... */
};

uint8_t crc8_fast(const uint8_t *data, size_t len) {
    uint8_t crc = 0xFF; // Початкове значення
    for (size_t i = 0; i < len; ++i) {
        crc = crc8_table[crc ^ data[i]];
    }
    return crc;
}
