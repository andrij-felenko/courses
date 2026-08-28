// --- ПІСЛЯ інлайну й розлучення: три чесні функції, кожна робить одне. ---

// Сирий кадр: старт, довжина, тіло, стоп. І все.
void send_raw(const uint8_t *payload, size_t len) {
    uint8_t frame[300];
    size_t  f = 0;
    frame[f++] = 0xAA;
    frame[f++] = (uint8_t)len;
    memcpy(frame + f, payload, len); f += len;
    frame[f++] = 0x55;
    hw_tx(frame, f);
}

// Кадр із CRC тіла. Помітно, що це просто raw + один байт контролю.
void send_crc(const uint8_t *payload, size_t len) {
    uint8_t frame[300];
    size_t  f = 0;
    frame[f++] = 0xAA;
    frame[f++] = (uint8_t)len;
    memcpy(frame + f, payload, len); f += len;
    frame[f++] = crc8(payload, len);   // ← єдина відмінність від raw
    frame[f++] = 0x55;
    hw_tx(frame, f);
}

// Кадр зі стисненим тілом. Тіло інше, конверт той самий.
void send_compressed(const uint8_t *payload, size_t len) {
    uint8_t body[256];
    size_t  n = rle_compress(payload, len, body);
    uint8_t frame[300];
    size_t  f = 0;
    frame[f++] = 0xAA;
    frame[f++] = (uint8_t)n;
    memcpy(frame + f, body, n); f += n;
    frame[f++] = 0x55;
    hw_tx(frame, f);
}
