static int map_file(const char *path, unsigned req_flags, int verbose)
{
    int fd = open(path, O_RDONLY);
    if (fd < 0) { perror(path); return -1; }

    struct stat st;
    if (fstat(fd, &st) < 0) { perror("fstat"); close(fd); return -1; }

    struct fiemap *fm = malloc(sizeof *fm + SLOTS * sizeof fm->fm_extents[0]);
    if (!fm) { fprintf(stderr, "бракує пам'яті\n"); close(fd); return -1; }

    struct walk w;
    memset(&w, 0, sizeof w);
    uint64_t want = 0, idx = 0;
    int last = 0, rc = 0;

    if (verbose)
        printf("       №     зсув у файлі      довжина    зсув на носії  прапорці\n");

    while (!last) {
        memset(fm, 0, sizeof *fm);
        fm->fm_start        = want;
        fm->fm_length       = FIEMAP_MAX_OFFSET - want;
        /* висаджувати кеш має сенс один раз, перед першим питанням */
        fm->fm_flags        = want ? (req_flags & ~FIEMAP_FLAG_SYNC) : req_flags;
        fm->fm_extent_count = SLOTS;

        if (ioctl(fd, FS_IOC_FIEMAP, fm) < 0) {
            if (errno == EBADR)
                fprintf(stderr, "%s: ФС не розуміє прапорці 0x%x\n", path, fm->fm_flags);
            else if (errno == EOPNOTSUPP)
                fprintf(stderr, "%s: ця файлова система не віддає карту\n", path);
            else
                fprintf(stderr, "%s: FIEMAP: %s\n", path, strerror(errno));
            rc = -1;
            break;
        }
        if (fm->fm_mapped_extents == 0)
            break;                                /* даних далі немає */

        for (unsigned i = 0; i < fm->fm_mapped_extents; i++) {
            const struct fiemap_extent *e = &fm->fm_extents[i];
            take(&w, e, verbose, ++idx);
            if (e->fe_flags & FIEMAP_EXTENT_LAST)
                last = 1;
        }

        if (w.seen_end <= want)                   /* карта не рухається */
            break;
        want = w.seen_end;
    }

    if (rc == 0 && w.seen_end < (uint64_t)st.st_size) {
        w.holes++;                                /* хвостова діра */
        w.hole_bytes += (uint64_t)st.st_size - w.seen_end;
    }

    if (rc == 0) {
        printf("%s\n", path);
        printf("  розмір               %" PRIu64 " Б\n", (uint64_t)st.st_size);
        printf("  віддано блоків       %" PRIu64 " Б\n", (uint64_t)st.st_blocks * 512);
        printf("  екстентів            %" PRIu64 "\n", w.n);
        if (w.n) {
            printf("  відображено          %" PRIu64 " Б\n", w.mapped);
            printf("  середня довжина      %.0f Б\n", (double)w.mapped / (double)w.n);
            printf("  найдовший            %" PRIu64 " Б\n", w.longest);
        }
        if (w.pairs)
            printf("  частка суцільності   %.3f (%" PRIu64 " з %" PRIu64
                   " сусідніх пар упритул)\n",
                   (double)w.glued / (double)w.pairs, w.glued, w.pairs);
        if (w.holes)     printf("  дірок                %" PRIu64 " на %" PRIu64 " Б\n",
                                w.holes, w.hole_bytes);
        if (w.unwritten) printf("  недоторканих         %" PRIu64 " Б (unwritten)\n", w.unwritten);
        if (w.delalloc)  printf("  ще не розподілено    %" PRIu64 " Б (delalloc)\n", w.delalloc);
        if (w.shared)    printf("  спільних із кимось   %" PRIu64 " Б (shared)\n", w.shared);
        if (w.encoded)   printf("  закодованих          %" PRIu64 " Б (encoded)\n", w.encoded);
    }

    free(fm);
    close(fd);
    return rc;
}
