int main(int argc, char **argv)
{
    pgsz = sysconf(_SC_PAGESIZE);
    unsigned long need = 0;
    const char *only = NULL;
    int want_hidden = 0;

    for (int i = 1; i < argc; i++) {
        if (!strcmp(argv[i], "--need") && i + 1 < argc)
            need = strtoul(argv[++i], NULL, 0);
        else if (!strcmp(argv[i], "--zone") && i + 1 < argc)
            only = argv[++i];
        else if (!strcmp(argv[i], "--hidden"))
            want_hidden = 1;
        else { fprintf(stderr, "не знаю опції %s\n", argv[i]); return 2; }
    }

    static char buf[BUFSZ], zi[BUFSZ];
    if (slurp("/proc/buddyinfo", buf, sizeof buf) < 0) { perror("buddyinfo"); return 1; }
    if (want_hidden && slurp("/proc/zoneinfo", zi, sizeof zi) < 0) zi[0] = '\0';

    static struct zonerow rows[MAX_ZONES];
    int nrows = 0;
    char *save = NULL;
    for (char *ln = strtok_r(buf, "\n", &save); ln && nrows < MAX_ZONES;
         ln = strtok_r(NULL, "\n", &save))
        if (parse_row(ln, &rows[nrows])) analyze(&rows[nrows++]);
    if (!nrows) { fprintf(stderr, "жодного рядка не розібрано\n"); return 1; }

    /* Порядок, потрібний під запит: найменший k, де 2ᵏ кадрів вистачає. */
    int wanted = -1;
    if (need) {
        wanted = 0;
        while ((unsigned long) pgsz << wanted < need && wanted < rows[0].norders - 1)
            wanted++;
    }

    char h1[32], h2[32];
    human((unsigned long) pgsz, h1, sizeof h1);
    human((unsigned long) pgsz << (rows[0].norders - 1), h2, sizeof h2);
    printf("кадр %s, порядків %d → MAX_PAGE_ORDER = %d, найбільший блок %s\n\n",
           h1, rows[0].norders, rows[0].norders - 1, h2);

    for (int i = 0; i < nrows; i++) {
        struct zonerow *r = &rows[i];
        if (only && strcmp(only, r->name)) continue;
        /* Ширину полів printf рівняє за БАЙТАМИ, а кирилична літера важить два,
           тож усі стовпці тут числові, а підписи — латиниця або кінець рядка. */
        printf("Node %d, zone %-8s  вільно %9.1f МіБ", r->node, r->name,
               r->free_pages * (double) pgsz / 1048576.0);
        if (r->top >= 0) {
            human((unsigned long) pgsz << r->top, h2, sizeof h2);
            printf("   найбільший блок: порядок %d = %s\n", r->top, h2);
        } else {
            printf("   вільних блоків немає зовсім\n");
        }

        if (want_hidden) {
            unsigned long hid = pcp_hidden(zi, r->node, r->name);
            human(hid * (unsigned long) pgsz, h1, sizeof h1);
            printf("    у запасах ядер, поза цим рядком: %lu кадрів (%s)\n", hid, h1);
        }

        if (need) {
            human(need, h1, sizeof h1);
            printf("    під %s треба порядок %d → таких блоків ще дістану: %lu\n",
                   h1, wanted, wanted < r->norders ? r->avail[wanted] : 0);
            continue;
        }

        if (!only) continue;                 /* таблиця за порядками — на прохання */
        puts("    порядок     кадрів     у списку   ще дістану   розмір");
        for (int k = 0; k < r->norders; k++) {
            human((unsigned long) pgsz << k, h1, sizeof h1);
            printf("    %7d %10lu %12lu %12lu   %s\n",
                   k, 1UL << k, r->nr_free[k], r->avail[k], h1);
        }
        putchar('\n');
    }
    return 0;
}
