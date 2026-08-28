static uint8_t crc8_table[256];

/* Будуємо таблицю ОДИН раз — тим самим бітовим циклом над значеннями 0…255. */
void crc8_build_table(void)
{
    for (int i = 0; i < 256; i++) {
        uint8_t crc = (uint8_t)i;
        for (int bit = 0; bit < 8; bit++)
            crc = (crc & 0x80) ? (uint8_t)((crc << 1) ^ 0x07)
                               : (uint8_t)(crc << 1);
        crc8_table[i] = crc;                   /* наслідок восьми тактів для байта i */
    }
}

/* Гарячий цикл: одне читання таблиці й один XOR на байт. */
uint8_t crc8_table_lookup(const uint8_t *data, size_t len,
                          uint8_t init, uint8_t xorout)
{
    uint8_t crc = init;
    for (size_t i = 0; i < len; i++) {
        uint8_t idx = crc ^ data[i];  /* ширші CRC: idx = (crc >> (width-8)) ^ byte */
        crc = crc8_table[idx];        /*            crc = (crc << 8) ^ T[idx]       */
    }
    return crc ^ xorout;
}
