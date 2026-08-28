static int replay(KV *kv) {
    uint8_t *rec = malloc(HDR + MAX_BODY);
    uint8_t trl[TRL];
    off_t good = 0;
    uint64_t expect = 1;
    int rc = -1;

    if (!rec) return -1;
    if (lseek(kv->fd, 0, SEEK_SET) < 0) goto out;

    for (;;) {
        ssize_t got = read_full(kv->fd, rec, HDR);
        if (got < 0) goto out;
        if (got < (ssize_t)HDR) break;               /* заголовок обірвано */

        uint32_t len = get_u32(rec + 4);
        uint64_t seq = get_u64(rec + 8);
        if (get_u32(rec) != MAGIC) break;            /* це не наш запис    */
        if (len < 5 || len > MAX_BODY) break;        /* довжина-сміття     */
        if (seq != expect) break;                    /* дірка в нумерації  */

        got = read_full(kv->fd, rec + HDR, len);
        if (got < 0) goto out;
        if (got < (ssize_t)len) break;               /* тіло не дописалося */

        got = read_full(kv->fd, trl, TRL);
        if (got < 0) goto out;
        if (got < (ssize_t)TRL) break;               /* печатки немає      */
        if (get_u32(trl + 4) != SEAL) break;         /* печатка не та      */
        if (get_u32(trl) != crc32(rec, HDR + len)) break;   /* сума не та  */

        uint8_t  op   = rec[HDR];
        uint32_t klen = get_u32(rec + HDR + 1);
        if ((op != OP_PUT && op != OP_DEL) || klen > len - 5) break;

        const uint8_t *key = rec + HDR + 5;
        if (apply(kv, op, key, klen, key + klen, len - 5 - klen) < 0) goto out;

        good = lseek(kv->fd, 0, SEEK_CUR);           /* кінець цього запису */
        if (good < 0) goto out;
        expect = seq + 1;
    }

    /* усе після останнього справного запису — незапечатаний хвіст */
    if (ftruncate(kv->fd, good) < 0) goto out;
    if (lseek(kv->fd, good, SEEK_SET) < 0) goto out;
    kv->end = good;
    kv->next_seq = expect;
    rc = 0;
out:
    free(rec);
    return rc;
}

static int fsync_dir_of(const char *path) {
    char *copy = strdup(path);          /* dirname має право зіпсувати аргумент */
    if (!copy) return -1;
    int fd = open(dirname(copy), O_RDONLY | O_DIRECTORY);
    free(copy);
    if (fd < 0) return -1;
    int rc = fsync(fd);
    if (close(fd) < 0) rc = -1;
    return rc;
}

static int kv_open(KV *kv, const char *path, int durable) {
    memset(kv, 0, sizeof *kv);
    kv->durable = durable;
    kv->fd = open(path, O_RDWR | O_CREAT, 0644);
    if (kv->fd < 0) return -1;
    /* Файл щойно могли створити. Його власний fsync не робить тривким ІМ'Я:
       запис у каталозі — окремі метадані, і без цього після обриву
       можна отримати цілий журнал, на який ніщо не вказує. */
    if (durable && fsync_dir_of(path) < 0) { close(kv->fd); return -1; }
    if (replay(kv) < 0) { close(kv->fd); return -1; }
    return 0;
}

static void kv_close(KV *kv) {
    for (size_t i = 0; i < kv->n; i++) { free(kv->tab[i].key); free(kv->tab[i].val); }
    free(kv->tab);
    close(kv->fd);
}
