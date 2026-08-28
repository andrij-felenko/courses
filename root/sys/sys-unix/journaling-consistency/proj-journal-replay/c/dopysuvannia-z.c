static int kv_put(KV *kv, uint8_t op, const uint8_t *key, uint32_t klen,
                  const uint8_t *val, uint32_t vlen) {
    uint32_t len = 5 + klen + vlen;
    if (len > MAX_BODY) { errno = EMSGSIZE; return -1; }

    size_t total = HDR + len + TRL;
    uint8_t *rec = malloc(total);
    if (!rec) return -1;

    put_u32(rec,      MAGIC);
    put_u32(rec + 4,  len);
    put_u64(rec + 8,  kv->next_seq);
    rec[HDR] = op;
    put_u32(rec + HDR + 1, klen);
    if (klen) memcpy(rec + HDR + 5,        key, klen);
    if (vlen) memcpy(rec + HDR + 5 + klen, val, vlen);
    put_u32(rec + HDR + len,     crc32(rec, HDR + len));
    put_u32(rec + HDR + len + 4, SEAL);

    if (write_full(kv->fd, rec, total) < 0) {
        /* Огризок треба прибрати ЗАРАЗ: якщо лишити його й дописати
           наступний запис за ним, відтворення спиниться на смітті
           й не дійде до всього, що після нього. */
        int e = errno;
        (void)ftruncate(kv->fd, kv->end);
        (void)lseek(kv->fd, kv->end, SEEK_SET);
        free(rec);
        errno = e;
        return -1;
    }
    free(rec);

    if (kv->durable && fdatasync(kv->fd) < 0) {
        /* Помилку fsync не можна ні проковтнути, ні «перепитати»: ядро
           повідомляє про неї один раз, і повторний виклик поверне успіх,
           хоча дані так і не лягли. Єдина чесна відповідь — упасти. */
        perror("fdatasync");
        _exit(70);
    }
    /* лише тут запис вважається підтвердженим */

    if (apply(kv, op, key, klen, val, vlen) < 0) { perror("apply"); _exit(70); }
    kv->next_seq++;
    kv->end += (off_t)total;
    return 0;
}
