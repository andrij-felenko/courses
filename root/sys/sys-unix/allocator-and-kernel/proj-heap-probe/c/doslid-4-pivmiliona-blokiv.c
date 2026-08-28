#define BLOCKS 512000

static void snapshot(const char *tag)
{
    printf("      VmRSS = %8ld КіБ   VmSize = %8ld КіБ   брейк = %p   %s\n",
           rss_kib(), vsize_kib(), brk_now(), tag);
}

static void probe_trapped(void)
{
    void **v;
    size_t i;

    printf("[4] півмільйона блоків, звільнено всі, крім верхнього\n");
    snapshot("старт");

    v = xmalloc(BLOCKS * sizeof *v);
    for (i = 0; i < BLOCKS; i++) {
        v[i] = xmalloc(1 * KiB);
        memset(v[i], 0x5a, 1 * KiB);      /* доторкнутися: без цього сторінок не буде */
    }
    snapshot("512000 блоків по 1 КіБ виділено й заповнено");

    for (i = 0; i + 1 < BLOCKS; i++)
        free(v[i]);
    snapshot("free() усіх, крім верхнього");

    malloc_trim(0);
    snapshot("після malloc_trim(0)");

    free(v[BLOCKS - 1]);
    snapshot("після free() верхнього");

    free(v);
}
