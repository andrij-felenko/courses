/* «Node 0, zone   Normal   88214   19842   6120 …»
   Після назви зони — усі числа до кінця рядка, і скільки їх, вирішує ядро. */
static int parse_row(const char *s, struct zonerow *r)
{
    char *end;
    const char *p = strstr(s, "Node ");
    if (!p) return 0;
    r->node = (int) strtol(p + 5, &end, 10);
    p = end;

    p = strstr(p, "zone");
    if (!p) return 0;
    p += 4;
    while (*p == ' ' || *p == '\t') p++;
    size_t n = strcspn(p, " \t");
    if (n == 0 || n >= sizeof r->name) return 0;
    memcpy(r->name, p, n);
    r->name[n] = '\0';
    p += n;

    r->norders = 0;
    while (r->norders < MAX_ORDERS) {
        unsigned long v = strtoul(p, &end, 10);
        if (end == p) break;             /* чисел більше немає — рядок скінчився */
        r->nr_free[r->norders++] = v;
        p = end;
    }
    return r->norders > 0;
}

/* avail(k) = 2·avail(k+1) + nr_free[k] — одним проходом згори вниз. */
static void analyze(struct zonerow *r)
{
    unsigned long acc = 0;
    for (int k = r->norders - 1; k >= 0; k--) {
        acc = acc * 2 + r->nr_free[k];
        r->avail[k] = acc;
    }
    r->free_pages = r->avail[0];         /* блок будь-якого порядку — це кадри */
    r->top = -1;
    for (int k = 0; k < r->norders; k++)
        if (r->nr_free[k]) r->top = k;
}
