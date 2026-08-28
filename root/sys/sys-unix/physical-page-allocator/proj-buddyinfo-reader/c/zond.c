int main(int argc, char **argv)
{
    long pg = sysconf(_SC_PAGESIZE);
    long hp = sysfs_num(THP "hpage_pmd_size");
    if (hp <= 0) {
        fprintf(stderr, "прозорих великих сторінок у цьому ядрі немає\n");
        return 1;
    }
    size_t hpsz = (size_t) hp;
    int pmd_order = 0;
    for (size_t s = (size_t) pg; s < hpsz; s <<= 1) pmd_order++;

    size_t count = 128;
    int collapse = 0;
    for (int i = 1; i < argc; i++) {
        if (!strcmp(argv[i], "--count") && i + 1 < argc) count = strtoul(argv[++i], NULL, 0);
        else if (!strcmp(argv[i], "--collapse")) collapse = 1;
        else { fprintf(stderr, "не знаю опції %s\n", argv[i]); return 2; }
    }

    size_t total = count * hpsz;
    printf("велика сторінка %zu Б = порядок %d; прошу %zu штук (%.1f МіБ)\n",
           hpsz, pmd_order, count, total / 1048576.0);

    void *raw = mmap(NULL, total + hpsz, PROT_READ | PROT_WRITE,
                     MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if (raw == MAP_FAILED) { perror("mmap"); return 1; }
    /* вирівнювання на межу великої сторінки — умова, а не оптимізація:
       без нього великого запису таблиці не буде за жодної форми пам'яті */
    volatile unsigned char *base =
        (volatile unsigned char *) (((uintptr_t) raw + hpsz - 1) & ~(uintptr_t)(hpsz - 1));

    long a0 = vmstat("thp_fault_alloc"), f0 = vmstat("thp_fault_fallback");
    long s0 = vmstat("compact_stall"),   c0 = vmstat("compact_success");
    long thp0 = anon_thp_kb();                  /* що в процесі вже було до нас */

    double *us = malloc(count * sizeof *us);
    size_t ok = 0, enomem = 0, other = 0;

    if (collapse) {
        /* Спершу набираємо звичайні кадри. Це має сенс, лише коли
           transparent_hugepage/enabled = madvise: при «always» ядро вже
           на дотику дасть велику сторінку, і збирати буде нічого. */
        for (size_t i = 0; i < count; i++)
            for (size_t off = 0; off < hpsz; off += (size_t) pg)
                base[i * hpsz + off] = 0xA5;
        for (size_t i = 0; i < count; i++) {
            double t = now_us();
            int rc = madvise((void *) (base + i * hpsz), hpsz, MADV_COLLAPSE);
            us[i] = now_us() - t;
            if (rc == 0) ok++;
            else if (errno == ENOMEM) enomem++;     /* блоку порядку 9 не склалося */
            else other++;
        }
    } else {
        madvise((void *) base, total, MADV_HUGEPAGE);
        for (size_t i = 0; i < count; i++) {
            double t = now_us();
            base[i * hpsz] = 0xA5;                  /* один дотик на шматок */
            us[i] = now_us() - t;
        }
        /* smaps_rollup підсумовує ВЕСЬ процес, тому рахуємо приріст, а не
           повне число: великі сторінки могла мати й арена алокатора. */
        long got = anon_thp_kb() - (thp0 > 0 ? thp0 : 0);
        ok = got > 0 ? (size_t) got / (hpsz / 1024) : 0;
        if (ok > count) ok = count;
        enomem = count - ok;                        /* тиха відмова — це просто решта */
    }

    qsort(us, count, sizeof *us, cmp_d);
    printf("дано великих сторінок: %zu з %zu   (відмов: %zu, інших помилок: %zu)\n",
           ok, count, enomem, other);
    printf("затримка на шматок, мкс: медіана %.1f, 90%% %.1f, найгірша %.1f\n",
           us[count / 2], us[count * 9 / 10], us[count - 1]);
    printf("приріст: thp_fault_alloc %+ld, thp_fault_fallback %+ld, "
           "compact_stall %+ld, compact_success %+ld\n",
           vmstat("thp_fault_alloc") - a0, vmstat("thp_fault_fallback") - f0,
           vmstat("compact_stall") - s0, vmstat("compact_success") - c0);

    free(us);
    munmap(raw, total + hpsz);
    return 0;
}
