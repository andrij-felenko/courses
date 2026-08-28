// ЧИТАННЯ: зазирнути в покажчик, стрибнути за зсувом, віддати значення.
int store_get(const char *key, void *out, uint16_t *out_len) {
    uint8_t klen = (uint8_t)strnlen(key, KEY_LEN);
    index_ent_t *s = index_slot(key, klen);
    if (!s || !s->used) return -1;                   // ключа нема

    rec_hdr_t h;
    flash_read(s->offset, &h, sizeof h);             // стрибок ПРОСТО на потрібний запис
    flash_read(s->offset + sizeof h, out, h.val_len);
    *out_len = h.val_len;
    return 0;
}

// ЗАПИС: дописати новий запис у кінець, тоді оновити покажчик.
int store_put(const char *key, const void *val, uint16_t vlen) {
    uint8_t klen = (uint8_t)strnlen(key, KEY_LEN);
    if (write_off + rec_size(vlen) > LOG_SIZE) return -1;   // журнал повний → час ущільнювати

    uint32_t off = write_off;
    write_off = rec_write(off, key, klen, val, vlen);       // допис + печатка (атомарно)

    index_ent_t *s = index_slot(key, klen);                 // оновлюємо покажчик
    if (!s) return -1;                                      // місця в покажчику нема
    memcpy(s->key, key, KEY_LEN);
    s->offset = off;                                        // тепер ключ веде на НОВИЙ запис
    s->used = 1;
    return 0;
}
