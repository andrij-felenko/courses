/* ── контекст обходу ─────────────────────────────────────────────────── */

struct sparse_hit { char *path; uintmax_t gap, size, real; };

struct ctx {
    struct table seen;
    int          one_fs;
    dev_t        root_dev;

    uintmax_t dirs, files, symlinks, others;
    uintmax_t real_bytes, apparent_bytes, shared_bytes;
    uintmax_t errors, vanished, crossings, sparse_count;

    struct sparse_hit sparse[SPARSE_TOP];
};

static void warn_at(struct ctx *c, const char *path, const char *what)
{
    c->errors++;
    fprintf(stderr, "inodesum: %s: %s: %s\n", path, what, strerror(errno));
}

/* Розрив між номінальним і реальним обсягом — ознака дір. Саме ознака,
 * а не доказ: стиснення на рівні ФС дає такий самий розрив. */
static void note_sparse(struct ctx *c, const struct stat *st, const char *path)
{
    if (!S_ISREG(st->st_mode) || st->st_size <= 0)
        return;

    uintmax_t size = (uintmax_t)st->st_size;
    uintmax_t real = (uintmax_t)st->st_blocks * BLOCK_UNIT;
    if (real >= size / 2 || size - real < ((uintmax_t)1 << 20))
        return;                     /* менш ніж половина дір або менш ніж МіБ */

    uintmax_t gap = size - real;
    c->sparse_count++;

    size_t worst = 0;
    for (size_t i = 1; i < SPARSE_TOP; i++)
        if (c->sparse[i].gap < c->sparse[worst].gap) worst = i;
    if (c->sparse[worst].gap >= gap)
        return;

    free(c->sparse[worst].path);
    c->sparse[worst].path = strdup(path);
    c->sparse[worst].gap  = gap;
    c->sparse[worst].size = size;
    c->sparse[worst].real = real;
}

static void account(struct ctx *c, const struct stat *st, const char *path)
{
    uintmax_t real = (uintmax_t)st->st_blocks * BLOCK_UNIT;
    uintmax_t size = (uintmax_t)st->st_size;

    if (S_ISDIR(st->st_mode)) {
        c->dirs++;
        c->real_bytes     += real;      /* каталог теж займає блоки */
        c->apparent_bytes += size;
        return;                         /* жорстко зв'язати каталог не можна */
    }

    if      (S_ISREG(st->st_mode)) c->files++;
    else if (S_ISLNK(st->st_mode)) c->symlinks++;
    else                           c->others++;

    /* Єдине ім'я — файл не може трапитися вдруге, у таблицю не кладемо.
     * Саме це рішення тримає таблицю в тисячах записів, а не в мільйонах. */
    if (st->st_nlink <= 1 || table_first_time(&c->seen, st, path)) {
        c->real_bytes     += real;
        c->apparent_bytes += size;
        note_sparse(c, st, path);
    } else {
        c->shared_bytes += real;        /* стільки додав би наївний обхід */
    }
}
