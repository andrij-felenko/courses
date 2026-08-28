// Мінімальний CRC-16/CCITT (поліном 0x1021) — для прикладу побайтово.
// У прошивці частіше беруть табличний варіант заради швидкості.
static uint16_t crc16_ccitt(const uint8_t *p, size_t n) {
    uint16_t crc = 0xFFFF;
    for (size_t i = 0; i < n; i++) {
        crc ^= (uint16_t)p[i] << 8;
        for (int k = 0; k < 8; k++)
            crc = (crc & 0x8000) ? (uint16_t)((crc << 1) ^ 0x1021)
                                 : (uint16_t)(crc << 1);
    }
    return crc;
}

// сюди приймач кладе те, що робити з валідним кадром
extern void handle_frame(const uint8_t *data, size_t len);

static void frame_complete(frame_rx_t *rx) {
    if (rx->len < 3)                        // кадр коротший за 1 байт даних + 2 CRC — брак
        return;

    size_t body = rx->len - 2;              // тіло без двох байтів CRC
    uint16_t got  = ((uint16_t)rx->buf[body] << 8) | rx->buf[body + 1];  // CRC із кадру (big-endian)
    uint16_t calc = crc16_ccitt(rx->buf, body);                          // рахуємо самі

    if (got == calc)                        // сума зійшлася — кадр цілий
        handle_frame(rx->buf, body);        // віддаємо тіло логіці
    // не зійшлася — тихо відкидаємо: приймач уже в WAIT, чекає наступного FLAG
}
