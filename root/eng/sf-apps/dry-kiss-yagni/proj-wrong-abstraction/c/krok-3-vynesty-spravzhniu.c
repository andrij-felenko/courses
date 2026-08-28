// --- Справжня спільність: збирання конверта. Приватний хелпер (static). ---
// Кладе старт, довжину і тіло у frame; повертає, скільки байтів уже лежить.
// Стоп-байт (і опційний CRC перед ним) кожна функція дописує САМА —
// хелпер не знає й не вирішує, хто його кличе.
static size_t envelope_begin(uint8_t *frame,
                             const uint8_t *body, size_t n) {
    size_t f = 0;
    frame[f++] = 0xAA;                 // старт
    frame[f++] = (uint8_t)n;           // довжина тіла
    memcpy(frame + f, body, n); f += n;
    return f;                          // курсор: скільки вже записано
}

void send_raw(const uint8_t *payload, size_t len) {
    uint8_t frame[300];
    size_t  f = envelope_begin(frame, payload, len);
    frame[f++] = 0x55;                 // стоп — дописую сам
    hw_tx(frame, f);
}

void send_crc(const uint8_t *payload, size_t len) {
    uint8_t frame[300];
    size_t  f = envelope_begin(frame, payload, len);
    frame[f++] = crc8(payload, len);   // свій байт CRC — явно, тут
    frame[f++] = 0x55;
    hw_tx(frame, f);
}

void send_compressed(const uint8_t *payload, size_t len) {
    uint8_t body[256];
    size_t  n = rle_compress(payload, len, body);
    uint8_t frame[300];
    size_t  f = envelope_begin(frame, body, n);   // тіло вже стиснене
    frame[f++] = 0x55;
    hw_tx(frame, f);
}
