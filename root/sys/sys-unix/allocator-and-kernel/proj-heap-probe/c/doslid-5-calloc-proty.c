static void probe_calloc(void)
{
    const size_t SZ = 1024 * MiB;
    volatile unsigned long sink = 0;
    unsigned char *a, *b;
    long r0, r1, r2, r3;
    double t0, t1, t2, t3, t4, t5;
    size_t i;

    printf("[5] calloc проти malloc+memset на 1 ГіБ\n");
    r0 = rss_kib();

    t0 = now_s();
    a = calloc(1, SZ);
    t1 = now_s();
    r1 = rss_kib();
    if (!a) { printf("      calloc не вдався\n"); return; }
    printf("      calloc(1, 1 ГіБ)          %9.3f мс   VmRSS %+8ld КіБ\n",
           (t1 - t0) * 1e3, r1 - r0);

    t2 = now_s();
    for (i = 0; i < SZ; i += 4096)
        sink += a[i];
    t3 = now_s();
    r2 = rss_kib();
    printf("      прочитати всі сторінки    %9.3f мс   VmRSS %+8ld КіБ   (сума = %lu)\n",
           (t3 - t2) * 1e3, r2 - r1, sink);

    t4 = now_s();
    b = opaque(malloc(SZ));
    if (!b) { printf("      malloc не вдався\n"); free(a); return; }
    memset(b, 0, SZ);
    t5 = now_s();
    r3 = rss_kib();
    printf("      malloc + memset(1 ГіБ)    %9.3f мс   VmRSS %+8ld КіБ\n",
           (t5 - t4) * 1e3, r3 - r2);

    free(a);
    free(b);
}
