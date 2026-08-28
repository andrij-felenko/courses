static int cmp_d(const void *a, const void *b)
{
    double x = *(const double *)a, y = *(const double *)b;
    return (x > y) - (x < y);
}

static void exp_latency(int lock)
{
    size_t n = 64UL * 1024 * 1024 / PGSZ;        /* 16384 сторінки */
    size_t len = n * PGSZ;
    double *lat = malloc(n * sizeof *lat);

    char *p = mmap(NULL, len, PROT_READ | PROT_WRITE,
                   MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    madvise(p, len, MADV_NOHUGEPAGE);
    if (lock) {
        mlockall(MCL_CURRENT | MCL_FUTURE);      /* див. ulimit -l */
        touch_seq(p, len, 1);                    /* усі збої — тут, на старті */
    }

    for (size_t i = 0; i < n; i++) {
        double t0 = now();
        p[i * PGSZ] = 1;
        lat[i] = (now() - t0) * 1e6;             /* мкс */
    }
    qsort(lat, n, sizeof *lat, cmp_d);
    printf("  %-24s медіана %6.2f   99.9%% %7.2f   максимум %8.2f мкс\n",
           lock ? "mlockall + прогрів" : "без mlock, перший дотик",
           lat[n / 2], lat[(size_t)(n * 0.999)], lat[n - 1]);
    free(lat);
    if (lock) munlockall();
    munmap(p, len);
}
