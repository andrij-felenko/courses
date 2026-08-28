static int by_pss(const void *a, const void *b)
{
    const struct region *x = a, *y = b;
    if (x->pss == y->pss) return 0;
    return x->pss < y->pss ? 1 : -1;         /* спадання */
}

static void report_pid(long pid, int top)
{
    char path[64];
    snprintf(path, sizeof path, "/proc/%ld/smaps", pid);

    size_t len;
    char *buf = slurp(path, &len);
    if (!buf) {
        fprintf(stderr, "pid %ld: %s\n", pid, strerror(errno));
        return;
    }

    memset(tab, 0, sizeof tab);
    tab_used = 0;
    parse_smaps(buf, len);
    free(buf);

    if (tab_used == 0)
        return;                              /* ядрова нитка: карти немає */

    struct region *list = malloc(tab_used * sizeof *list);
    if (!list) return;

    unsigned m = 0;
    unsigned long vsz = 0, rss = 0, pss = 0, uss = 0, swap = 0, spss = 0;

    for (unsigned i = 0; i < TAB_SZ; i++) {
        if (tab[i].name[0] == '\0')
            continue;
        list[m++] = tab[i];
        vsz  += tab[i].size;
        rss  += tab[i].rss;
        pss  += tab[i].pss;
        uss  += tab[i].priv_clean + tab[i].priv_dirty;
        swap += tab[i].swap;
        spss += tab[i].swap_pss;
    }
    qsort(list, m, sizeof *list, by_pss);

    printf("pid %ld  ділянок зведено в %u імен\n", pid, m);
    printf("VSZ %lu кБ   RSS %lu кБ   PSS %lu кБ   USS %lu кБ"
           "   Swap %lu кБ   SwapPSS %lu кБ\n\n",
           vsz, rss, pss, uss, swap, spss);

    printf("%10s %10s %10s %10s  %s\n", "PSS", "RSS", "USS", "Swap", "ділянка");
    for (unsigned i = 0; i < m && i < (unsigned)top; i++)
        printf("%10lu %10lu %10lu %10lu  %s\n",
               list[i].pss, list[i].rss,
               list[i].priv_clean + list[i].priv_dirty,
               list[i].swap, list[i].name);
    free(list);
}
