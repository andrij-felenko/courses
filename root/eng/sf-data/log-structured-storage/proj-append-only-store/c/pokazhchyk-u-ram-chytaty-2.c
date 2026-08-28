static uint32_t write_off;    // куди піде наступний допис (кінець журналу)

// Відбудувати покажчик і знайти кінець журналу. Кличеться один раз при старті.
void store_mount(void) {
    memset(index, 0, sizeof index);
    uint32_t off = 0;

    while (off + sizeof(rec_hdr_t) <= LOG_SIZE) {
        rec_hdr_t h;
        flash_read(off, &h, sizeof h);
        if (h.magic != MAGIC) break;                 // далі — чиста стерта пам'ять

        uint32_t need = rec_size(h.val_len);
        if (off + need > LOG_SIZE) break;            // запис не влазить — це хвіст

        // Перевіряємо печатку: читаємо збережений CRC і рахуємо свій.
        uint32_t stored;
        flash_read(off + sizeof h + h.val_len, &stored, sizeof stored);
        uint8_t buf[sizeof h + MAX_VAL];
        flash_read(off, buf, sizeof h + h.val_len);
        if (crc32(buf, sizeof h + h.val_len) != stored)
            break;                                   // печатка не сходиться → обірваний запис, СТОП

        // Запис дійсний → оновлюємо покажчик найновішим зсувом цього ключа.
        index_ent_t *s = index_slot(h.key, h.key_len);
        if (s) { memcpy(s->key, h.key, KEY_LEN); s->offset = off; s->used = 1; }

        off += need;                                 // крок до наступного запису
    }
    write_off = off;                                 // кінець журналу = точка допису
}
