// Записати один запис у журнал за зсувом off. Повертає новий зсув (за печаткою).
static uint32_t rec_write(uint32_t off, const char *key, uint8_t klen,
                          const void *val, uint16_t vlen) {
    rec_hdr_t h = { .magic = MAGIC, .key_len = klen, .val_len = vlen };
    memset(h.key, 0, KEY_LEN);
    memcpy(h.key, key, klen);

    // Печатку рахуємо з УСЬОГО, що лежатиме перед нею: заголовок + значення.
    uint32_t crc = crc32(&h, sizeof h);
    crc = crc32_update(crc, val, vlen);   // продовжуємо суму по значенню

    // Кладемо в пам'ять по черзі; печатка — ОСТАННЯ.
    flash_write(off,                    &h,  sizeof h);          // 1) заголовок
    flash_write(off + sizeof h,         val, vlen);             // 2) значення
    flash_write(off + sizeof h + vlen,  &crc, sizeof crc);      // 3) ПЕЧАТКА
    return off + rec_size(vlen);
}
