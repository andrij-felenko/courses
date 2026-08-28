static unsigned long sink;        /* щоб читання не виглядало марним */

static void touch(void *base, size_t bytes, size_t step, unsigned pause_ms,
                  int read_only, int release)
{
    volatile unsigned char *p = base;      /* без volatile запис можуть викинути */
    unsigned long acc = 0;
    char tag[48];

    for (size_t off = 0; off < bytes; off += step) {
        size_t end = off + step < bytes ? off + step : bytes;

        printf("%s @%.2f ГіБ …\n", read_only ? "читаю" : "пишу", off / (double) GIB);

        for (size_t i = off; i < end; i += pgsz)
            if (read_only) acc += p[i];    /* читання сторінки НЕ народить */
            else           p[i] = 0xA5;    /* запис — ось тут народить      */

        snprintf(tag, sizeof tag, "+%.2f ГіБ", end / (double) GIB);
        snap(tag);

        if (release) {                     /* madvise хоче адресу, вирівняну */
            uintptr_t a = ((uintptr_t) base + off + pgsz - 1) & ~(uintptr_t)(pgsz - 1);
            uintptr_t b = ((uintptr_t) base + end)            & ~(uintptr_t)(pgsz - 1);
            if (b > a) madvise((void *) a, b - a, MADV_DONTNEED);
        }
        if (pause_ms) {
            struct timespec ts = { pause_ms / 1000,
                                   (long)(pause_ms % 1000) * 1000000L };
            nanosleep(&ts, NULL);
        }
    }
    sink = acc;
}
