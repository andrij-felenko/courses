/* CRC-16/Modbus, напівбайтова таблиця: 16 записів × 2 Б = 32 байти у флеші.
   Профіль: поліном 0x8005 (відбитий — 0xA001), старт 0xFFFF, відбиття входу й виходу. */
static const uint16_t nib[16] = {
    0x0000, 0xCC01, 0xD801, 0x1400, 0xF001, 0x3C00, 0x2800, 0xE401,
    0xA001, 0x6C00, 0x7800, 0xB401, 0x5000, 0x9C01, 0x8801, 0x4400,
};

uint16_t crc16_modbus_update(uint16_t crc, const uint8_t *p, size_t n) {
    while (n--) {
        uint8_t b = *p++;
        crc = (uint16_t)(crc >> 4) ^ nib[(crc ^ b) & 0x0F];         /* спершу молодший півбайт */
        crc = (uint16_t)(crc >> 4) ^ nib[(crc ^ (b >> 4)) & 0x0F];  /* тоді старший */
    }
    return crc;
}
