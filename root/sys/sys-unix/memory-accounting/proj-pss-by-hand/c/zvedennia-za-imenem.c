struct region {
    char name[128];
    unsigned long size, rss, pss, priv_clean, priv_dirty, swap, swap_pss;
};

#define TAB_SZ 2048u                         /* степінь двійки, з великим запасом */
static struct region tab[TAB_SZ];
static unsigned      tab_used;

/* Комірка для імені (створює за потреби). NULL — таблиця переповнена. */
static struct region *bucket(const char *name, size_t n)
{
    if (n >= sizeof tab[0].name)
        n = sizeof tab[0].name - 1;

    unsigned long h = 1469598103934665603UL;             /* FNV-1a */
    for (size_t i = 0; i < n; i++) {
        h ^= (unsigned char)name[i];
        h *= 1099511628211UL;
    }

    for (unsigned i = (unsigned)(h & (TAB_SZ - 1)); ; i = (i + 1) & (TAB_SZ - 1)) {
        if (tab[i].name[0] == '\0') {
            if (tab_used * 4 >= TAB_SZ * 3)
                return NULL;                             /* заповнення > 75 % */
            memcpy(tab[i].name, name, n);
            tab[i].name[n] = '\0';
            tab_used++;
            return &tab[i];
        }
        if (strncmp(tab[i].name, name, n) == 0 && tab[i].name[n] == '\0')
            return &tab[i];
    }
}

/* Поле smaps → лічильник у struct region. Ключ порівнюємо ЦІЛКОМ. */
static const struct { const char *key; unsigned char len; size_t off; } FIELDS[] = {
    { "Size",           4, offsetof(struct region, size)       },
    { "Rss",            3, offsetof(struct region, rss)        },
    { "Pss",            3, offsetof(struct region, pss)        },
    { "Private_Clean", 13, offsetof(struct region, priv_clean) },
    { "Private_Dirty", 13, offsetof(struct region, priv_dirty) },
    { "Swap",           4, offsetof(struct region, swap)       },
    { "SwapPss",        7, offsetof(struct region, swap_pss)   },
};
