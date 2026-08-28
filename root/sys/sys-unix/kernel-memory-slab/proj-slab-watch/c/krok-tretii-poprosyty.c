static int drop_slab(void)          /* 2 — лише слабові кеші, без сторінкового */
{
    int fd = open("/proc/sys/vm/drop_caches", O_WRONLY);
    if (fd < 0) {
        fprintf(stderr, "drop_caches: %s (треба root)\n", strerror(errno));
        return -1;
    }
    sync();
    ssize_t w = write(fd, "2\n", 2);
    close(fd);
    if (w < 0) { perror("drop_caches"); return -1; }
    sleep(1);                       /* зменшувачам треба мить доробити */
    return 0;
}

static int cmd_squeeze(unsigned long want_mib)
{
    const size_t chunk = 512ul << 20;
    size_t n = (size_t)((want_mib + 511) / 512), got = 0;
    void **blk = calloc(n, sizeof *blk);
    if (!blk) return 1;

    unsigned long floor_kb = meminfo_kb("MemTotal") / 20;   /* 5 % — далі стоп */
    if (floor_kb < 256u * 1024) floor_kb = 256u * 1024;

    puts(" узято MemAvailable       dentry     слабів SReclaimable");
    for (size_t i = 0; i < n; i++) {
        void *m = mmap(NULL, chunk, PROT_READ | PROT_WRITE,
                       MAP_PRIVATE | MAP_ANONYMOUS | MAP_NORESERVE, -1, 0);
        if (m == MAP_FAILED) {
            fprintf(stderr, "mmap відмовив на %zu МіБ: %s\n",
                    got * 512, strerror(errno));
            break;
        }
        blk[got++] = m;
        for (size_t o = 0; o < chunk; o += PAGE)
            ((volatile char *)m)[o] = 1;     /* без запису сторінки не з'являться */

        if (read_slabinfo() < 0) break;
        const struct cache *d = find_cache("dentry");
        unsigned long avail = meminfo_kb("MemAvailable");
        printf("%6zu %12.0f %12lu %10lu %12.0f\n",
               got * 512, avail / 1024.0,
               d ? d->active_objs : 0, d ? d->num_slabs : 0,
               meminfo_kb("SReclaimable") / 1024.0);
        if (avail < floor_kb) {
            printf("вільного лишилося менш як %.0f МіБ — зупиняємось\n",
                   floor_kb / 1024.0);
            break;
        }
    }
    for (size_t k = 0; k < got; k++) munmap(blk[k], chunk);
    free(blk);
    return 0;
}
