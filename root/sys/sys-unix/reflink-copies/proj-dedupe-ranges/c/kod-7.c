int main(int argc, char **argv)
{
    int opt, measure = 0;
    while ((opt = getopt(argc, argv, "nmw:")) != -1) {
        switch (opt) {
        case 'n': dry_run = 1; break;
        case 'm': measure = 1; break;
        case 'w': win = (unsigned)strtoul(optarg, NULL, 10) * 1024u; break;
        default:  fprintf(stderr, "вжиток: %s [-n] [-m] [-w КіБ] каталог\n", argv[0]);
                  return 2;
        }
    }
    if (optind + 1 != argc || win < 4096 || win % 4096) {
        fprintf(stderr, "вжиток: %s [-n] [-m] [-w КіБ] каталог  (вікно кратне 4 КіБ)\n", argv[0]);
        return 2;
    }

    struct stat rt;
    if (stat(argv[optind], &rt) < 0) { perror(argv[optind]); return 1; }
    root_dev = rt.st_dev;

    pagesz   = (size_t)sysconf(_SC_PAGESIZE);
    max_dest = (unsigned)((pagesz - sizeof(struct file_dedupe_range)) /
                          sizeof(struct file_dedupe_range_info));
    if (max_dest > 128) max_dest = 128;         /* на 4 КіБ сторінці й так 127 */
    dfd = malloc(max_dest * sizeof *dfd);
    if (!dfd) { fprintf(stderr, "бракує пам'яті\n"); return 1; }

    if (nftw(argv[optind], visit, 64, FTW_PHYS) < 0) { perror("nftw"); return 1; }
    drop_hardlinks();

    if (measure) {
        uint64_t sh = 0;
        for (size_t i = 0; i < nfr; i++) sh += shared_bytes(fr[i].path);
        printf("файлів у дереві      %zu\n", nfr);
        printf("спільних байтів      %.1f ГіБ\n", (double)sh / (1024.0 * 1024 * 1024));
        return 0;
    }

    for (size_t i = 0; i < nfr; i++) hash_file((uint32_t)i);
    qsort(keys, nkeys, sizeof *keys, keycmp);

    uint64_t groups = 0;
    for (size_t i = 0; i < nkeys; ) {
        size_t j = i;
        while (j < nkeys && keys[j].h == keys[i].h) j++;
        if (j - i >= 2) { groups++; do_group(keys + i, j - i); }
        i = j;
    }

    printf("файлів у дереві      %zu\n", nfr);
    printf("вікон                %zu   (по %u КіБ)\n", nkeys, win / 1024);
    printf("груп однакових хешів %" PRIu64 "\n", groups);
    printf("кандидатів           %.1f ГіБ у %" PRIu64 " діапазонах\n",
           (double)g_asked / (1024.0 * 1024 * 1024), g_same + g_differs + g_failed);
    if (dry_run) { printf("(сухий прохід: нічого не змінено)\n"); return 0; }
    printf("злито (за ядром)     %.1f ГіБ\n", (double)g_moved / (1024.0 * 1024 * 1024));
    printf("status SAME          %" PRIu64 "\n", g_same);
    printf("status DIFFERS       %" PRIu64 "\n", g_differs);
    if (g_failed) printf("помилок              %" PRIu64 "\n", g_failed);
    return 0;
}
