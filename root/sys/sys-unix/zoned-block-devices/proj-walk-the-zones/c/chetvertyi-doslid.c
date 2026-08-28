/* Скільки зон пристрій дасть відкрити явно, поки не скаже «досить». */
static void probe_open_limit(int fd, uint32_t zsect, uint32_t nr)
{
    struct blk_zone_report *r = rep_alloc(BATCH);
    struct blk_zone_range rg;
    unsigned opened = 0, seen = 0;
    uint64_t sector = 0;

    while (seen < nr) {
        unsigned got = zones_report(fd, sector, BATCH, r);

        if (!got) break;
        for (unsigned i = 0; i < got; i++) {
            const struct blk_zone *z = &r->zones[i];

            if (z->type == BLK_ZONE_TYPE_CONVENTIONAL ||
                z->cond != BLK_ZONE_COND_EMPTY)
                continue;
            rg.sector = z->start;
            rg.nr_sectors = zsect;
            if (ioctl(fd, BLKOPENZONE, &rg) < 0) {
                printf("відкрито зон: %u; наступна — errno %d (%s)\n",
                       opened, errno, strerror(errno));
                free(r);
                return;
            }
            opened++;
        }
        sector = r->zones[got - 1].start + r->zones[got - 1].len;
        seen += got;
    }
    printf("відкрито зон: %u, ліміт не досягнуто\n", opened);
    free(r);
}
