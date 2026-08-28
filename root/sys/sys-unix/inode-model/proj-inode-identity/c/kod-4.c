/* ── звіт ────────────────────────────────────────────────────────────── */

static const char *human(uintmax_t bytes, char *buf, size_t n)
{
    static const char *unit[] = { "Б", "КіБ", "МіБ", "ГіБ", "ТіБ", "ПіБ" };
    double v = (double)bytes;
    size_t u = 0;
    while (v >= 1024.0 && u + 1 < sizeof unit / sizeof *unit) { v /= 1024.0; u++; }
    if (u == 0) snprintf(buf, n, "%ju Б", bytes);
    else        snprintf(buf, n, "%.1f %s", v, unit[u]);
    return buf;
}

static int cmp_group(const void *a, const void *b)
{
    const struct node *x = a, *y = b;
    uintmax_t wx = (x->seen - 1) * x->real, wy = (y->seen - 1) * y->real;
    return wx < wy ? 1 : (wx > wy ? -1 : 0);
}

static void report(struct ctx *c)
{
    char b[4][32];

    size_t ng = 0;
    for (size_t i = 0; i < c->seen.cap; i++)
        if (c->seen.slot[i].seen > 1) ng++;

    printf("\n──── підсумок ────\n");
    printf("каталогів               : %ju\n", c->dirs);
    printf("звичайних файлів        : %ju\n", c->files);
    printf("символьних посилань     : %ju\n", c->symlinks);
    printf("інших об'єктів          : %ju\n", c->others);
    printf("реальний обсяг          : %s   (Σ st_blocks·512, кожен inode раз)\n",
           human(c->real_bytes, b[0], sizeof b[0]));
    printf("номінальний обсяг       : %s   (Σ st_size)\n",
           human(c->apparent_bytes, b[1], sizeof b[1]));
    printf("подвійного обліку уникнуто: %s у %zu групах посилань\n",
           human(c->shared_bytes, b[2], sizeof b[2]), ng);
    if (c->crossings)  printf("меж монтування пропущено: %ju\n", c->crossings);
    if (c->vanished)   printf("зникло під час обходу   : %ju\n", c->vanished);
    if (c->errors)     printf("!! помилок              : %ju — підсумок НЕПОВНИЙ\n",
                              c->errors);

    if (ng > 0) {
        struct node *g = malloc(ng * sizeof *g);
        if (g != NULL) {
            size_t k = 0;
            for (size_t i = 0; i < c->seen.cap; i++)
                if (c->seen.slot[i].seen > 1) g[k++] = c->seen.slot[i];
            qsort(g, ng, sizeof *g, cmp_group);

            printf("\n──── найбільші групи посилань (імен у дереві / усього) ────\n");
            for (size_t i = 0; i < ng && i < 10; i++) {
                printf("  %10s  ×%ju/%ju  %s%s\n",
                       human((g[i].seen - 1) * g[i].real, b[3], sizeof b[3]),
                       g[i].seen, g[i].nlink,
                       g[i].first_path ? g[i].first_path : "(шлях не збережено)",
                       g[i].seen < g[i].nlink ? "   ← є імена ПОЗА деревом" : "");
            }
            free(g);
        }
    }

    if (c->sparse_count > 0) {
        printf("\n──── найдірявіші файли (%ju знайдено) ────\n", c->sparse_count);
        for (size_t i = 0; i < SPARSE_TOP; i++) {
            if (c->sparse[i].path == NULL) continue;
            printf("  розрив %s   номінально %s, реально %s\n  %s\n",
                   human(c->sparse[i].gap,  b[0], sizeof b[0]),
                   human(c->sparse[i].size, b[1], sizeof b[1]),
                   human(c->sparse[i].real, b[2], sizeof b[2]),
                   c->sparse[i].path);
        }
    }
}

int main(int argc, char **argv)
{
    struct ctx c;
    memset(&c, 0, sizeof c);
    if (!table_init(&c.seen, 1024)) { perror("calloc"); return 2; }

    int argi = 1;
    if (argi < argc && strcmp(argv[argi], "-x") == 0) { c.one_fs = 1; argi++; }
    if (argi >= argc) {
        fprintf(stderr, "вжиток: inodesum [-x] шлях...\n");
        return 2;
    }

    struct pathbuf p;
    memset(&p, 0, sizeof p);

    /* Таблиця одна на всі аргументи: інакше файл, зв'язаний із двох
     * названих дерев, порахувався б двічі. */
    for (; argi < argc; argi++) {
        if (!path_set(&p, argv[argi])) { perror("realloc"); return 2; }

        struct stat st;
        if (fstatat_retry(AT_FDCWD, p.s, &st, AT_SYMLINK_NOFOLLOW) != 0) {
            warn_at(&c, p.s, "fstatat");
            continue;
        }
        c.root_dev = st.st_dev;
        account(&c, &st, p.s);

        if (S_ISDIR(st.st_mode)) {
            int fd = openat_retry(AT_FDCWD, p.s, O_RDONLY | O_DIRECTORY | O_CLOEXEC);
            if (fd < 0) { warn_at(&c, p.s, "openat"); continue; }
            walk(fd, &p, &c);
        }
    }

    report(&c);
    free(p.s);
    return c.errors > 0 ? 1 : 0;
}
