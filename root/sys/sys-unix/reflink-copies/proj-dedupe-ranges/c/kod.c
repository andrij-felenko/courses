struct filerec {
    char     *path;
    uint64_t *h;        /* хеш кожного вікна; 0 — вікно пропущене */
    uint8_t  *merged;   /* вікно вже злите як призначення        */
    uint32_t  nwin;
    ino_t     ino;
};

struct key { uint64_t h; uint32_t f; uint32_t w; };

static struct filerec *fr;   static size_t nfr,   cfr;
static struct key     *keys; static size_t nkeys, ckeys;
static dev_t    root_dev;
static int      dry_run;
static size_t   pagesz;
static unsigned max_dest;    /* скільки призначень влазить в один виклик */
static int     *dfd;

static void *grow(void *p, size_t *cap, size_t need, size_t esz)
{
    if (need <= *cap) return p;
    size_t c = *cap ? *cap : 1024;
    while (c < need) c *= 2;
    void *q = realloc(p, c * esz);
    if (!q) { fprintf(stderr, "бракує пам'яті\n"); exit(1); }
    *cap = c;
    return q;
}
