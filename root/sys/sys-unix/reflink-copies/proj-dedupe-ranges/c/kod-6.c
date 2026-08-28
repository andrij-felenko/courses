static uint64_t shared_bytes(const char *path)
{
    enum { SLOTS = 256 };
    int fd = open(path, O_RDONLY);
    if (fd < 0) return 0;

    struct fiemap *fm = malloc(sizeof *fm + SLOTS * sizeof fm->fm_extents[0]);
    uint64_t shared = 0, want = 0, seen_end = 0;
    int last = 0;

    while (fm && !last) {
        memset(fm, 0, sizeof *fm);
        fm->fm_start        = want;
        fm->fm_length       = FIEMAP_MAX_OFFSET - want;
        fm->fm_flags        = want ? 0 : FIEMAP_FLAG_SYNC;
        fm->fm_extent_count = SLOTS;
        if (ioctl(fd, FS_IOC_FIEMAP, fm) < 0)  break;
        if (fm->fm_mapped_extents == 0)        break;

        for (unsigned i = 0; i < fm->fm_mapped_extents; i++) {
            const struct fiemap_extent *e = &fm->fm_extents[i];
            if (e->fe_logical + e->fe_length <= seen_end) continue;   /* уже бачили */
            if (e->fe_flags & FIEMAP_EXTENT_SHARED) shared += e->fe_length;
            seen_end = e->fe_logical + e->fe_length;
            if (e->fe_flags & FIEMAP_EXTENT_LAST) last = 1;
        }
        if (seen_end <= want) break;
        want = seen_end;
    }

    free(fm);
    close(fd);
    return shared;
}
