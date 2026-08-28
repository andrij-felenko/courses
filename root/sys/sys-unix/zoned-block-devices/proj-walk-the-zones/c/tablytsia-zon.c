/* Таблиця всіх зон пристрою. */
static void print_table(int fd, uint32_t nr)
{
    struct blk_zone_report *r = rep_alloc(BATCH);
    uint64_t sector = 0;
    unsigned seen = 0, idx = 0;

    puts(" зона    початок  довжина  ємність  вказівник  тип і стан");

    while (seen < nr) {
        unsigned got = zones_report(fd, sector, BATCH, r);

        if (!got) break;
        for (unsigned i = 0; i < got; i++) {
            const struct blk_zone *z = &r->zones[i];
            /* до ядра 5.9 поле ємності не заповнювали: нуль там значить
               «уся зона придатна», а не «нуль секторів» */
            uint64_t cap = z->capacity ? z->capacity : z->len;
            char wp[16];

            if (z->cond == BLK_ZONE_COND_EMPTY ||
                z->cond == BLK_ZONE_COND_IMP_OPEN ||
                z->cond == BLK_ZONE_COND_EXP_OPEN ||
                z->cond == BLK_ZONE_COND_CLOSED)
                snprintf(wp, sizeof wp, "+%llu",
                         (unsigned long long)(z->wp - z->start));
            else
                snprintf(wp, sizeof wp, "-");   /* вказівник недійсний */

            printf("%5u %10llu %8llu %8llu %10s  %s, %s\n", idx++,
                   (unsigned long long)z->start,
                   (unsigned long long)z->len,
                   (unsigned long long)cap, wp,
                   type_name(z->type), cond_name(z->cond));
        }
        sector = r->zones[got - 1].start + r->zones[got - 1].len;
        seen += got;
    }
    free(r);
}

/* Перша порожня послідовна зона — вона й буде піддослідною. */
static int find_target(int fd, uint32_t nr, struct blk_zone *out)
{
    struct blk_zone_report *r = rep_alloc(BATCH);
    uint64_t sector = 0;
    unsigned seen = 0;

    while (seen < nr) {
        unsigned got = zones_report(fd, sector, BATCH, r);

        if (!got) break;
        for (unsigned i = 0; i < got; i++)
            if (r->zones[i].type != BLK_ZONE_TYPE_CONVENTIONAL &&
                r->zones[i].cond == BLK_ZONE_COND_EMPTY) {
                *out = r->zones[i];
                free(r);
                return 1;
            }
        sector = r->zones[got - 1].start + r->zones[got - 1].len;
        seen += got;
    }
    free(r);
    return 0;
}
