/* ── таблиця тотожності (dev, ino) ───────────────────────────────────── */

struct node {
    dev_t     dev;
    ino_t     ino;
    uintmax_t nlink;       /* скільки імен має файл за словами inode */
    uintmax_t seen;        /* скільки з них ми зустріли в цьому дереві */
    uintmax_t size;
    uintmax_t real;        /* st_blocks · 512 */
    char     *first_path;  /* перше ім'я — щоб було що показати у звіті */
};

struct table { struct node *slot; size_t cap, used; };

/* seen == 0 означає «комірка вільна»: будь-який вставлений запис має
 * seen >= 1, тож окремий прапорець не потрібен. */

static uint64_t mix64(uint64_t h)
{
    h ^= h >> 33;
    h *= UINT64_C(0xff51afd7ed558ccd);
    h ^= h >> 33;
    h *= UINT64_C(0xc4ceb9fe1a85ec53);
    h ^= h >> 33;
    return h;
}

static uint64_t key_hash(dev_t dev, ino_t ino)
{
    return mix64((uint64_t)ino ^ mix64((uint64_t)dev));
}

static int table_init(struct table *t, size_t cap)   /* cap — степінь двійки */
{
    t->slot = calloc(cap, sizeof *t->slot);
    if (t->slot == NULL) return 0;
    t->cap = cap; t->used = 0;
    return 1;
}

static void table_put_raw(struct table *t, struct node n)
{
    size_t mask = t->cap - 1;
    size_t i = (size_t)key_hash(n.dev, n.ino) & mask;
    while (t->slot[i].seen != 0)
        i = (i + 1) & mask;
    t->slot[i] = n;
}

static int table_grow(struct table *t)
{
    struct table nt;
    if (!table_init(&nt, t->cap * 2)) return 0;
    for (size_t i = 0; i < t->cap; i++)
        if (t->slot[i].seen != 0)
            table_put_raw(&nt, t->slot[i]);
    nt.used = t->used;
    free(t->slot);
    *t = nt;
    return 1;
}

/* Повертає 1, якщо цей (dev, ino) трапився вперше — отже, його блоки
 * треба додати до підсумку; 0 — якщо це ще одне ім'я вже порахованого. */
static int table_first_time(struct table *t, const struct stat *st, const char *path)
{
    if ((t->used + 1) * 10 > t->cap * 7 && !table_grow(t))
        return 1;                       /* пам'ять скінчилася — рахуємо як нове */

    size_t mask = t->cap - 1;
    size_t i = (size_t)key_hash(st->st_dev, st->st_ino) & mask;
    while (t->slot[i].seen != 0) {
        if (t->slot[i].dev == st->st_dev && t->slot[i].ino == st->st_ino) {
            t->slot[i].seen++;
            return 0;
        }
        i = (i + 1) & mask;
    }

    t->slot[i].dev        = st->st_dev;
    t->slot[i].ino        = st->st_ino;
    t->slot[i].nlink      = (uintmax_t)st->st_nlink;
    t->slot[i].seen       = 1;
    t->slot[i].size       = (uintmax_t)st->st_size;
    t->slot[i].real       = (uintmax_t)st->st_blocks * BLOCK_UNIT;
    t->slot[i].first_path = strdup(path);   /* NULL тут не смертельний */
    t->used++;
    return 1;
}
