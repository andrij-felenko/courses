struct vma_stat {
    unsigned long rss, pss, ksm, swap;
    int mergeable, nohuge, found;
};

static void smaps_of(const void *addr, struct vma_stat *v)
{
    char line[512], perm[8];
    unsigned long lo, hi;
    int inside = 0;
    FILE *f;

    memset(v, 0, sizeof *v);
    if ((f = fopen("/proc/self/smaps", "r")) == NULL) return;

    while (fgets(line, sizeof line, f)) {
        /* Заголовок ділянки — єдиний рядок, де є ТРИ поля: межі й права.
           Рядки-значення на цей взірець не сідають. */
        if (sscanf(line, "%lx-%lx %7s", &lo, &hi, perm) == 3) {
            inside = (lo == (unsigned long)addr);
            v->found |= inside;
            continue;
        }
        if (!inside) continue;

        sscanf(line, "Rss: %lu kB",  &v->rss);
        sscanf(line, "Pss: %lu kB",  &v->pss);
        sscanf(line, "KSM: %lu kB",  &v->ksm);
        sscanf(line, "Swap: %lu kB", &v->swap);
        if (strncmp(line, "VmFlags:", 8) == 0) {
            v->mergeable = strstr(line, " mg") != NULL;
            v->nohuge    = strstr(line, " nh") != NULL;
        }
    }
    fclose(f);
}

struct proc_ksm {
    unsigned long rmap_items, merging_pages;
    long zero_pages, profit;
};

static int proc_ksm_read(struct proc_ksm *k)
{
    char line[128], name[64];
    long long val;
    FILE *f;

    memset(k, 0, sizeof *k);
    if ((f = fopen("/proc/self/ksm_stat", "r")) == NULL) return -1;

    while (fgets(line, sizeof line, f)) {
        if (sscanf(line, "%63s %lld", name, &val) != 2) continue;
        if      (!strcmp(name, "ksm_rmap_items"))     k->rmap_items    = (unsigned long)val;
        else if (!strcmp(name, "ksm_merging_pages"))  k->merging_pages = (unsigned long)val;
        else if (!strcmp(name, "ksm_zero_pages"))     k->zero_pages    = (long)val;
        else if (!strcmp(name, "ksm_process_profit")) k->profit        = (long)val;
    }
    fclose(f);
    return 0;
}

static unsigned long meminfo(const char *key)
{
    char line[256];
    unsigned long v = 0;
    size_t klen = strlen(key);
    FILE *f = fopen("/proc/meminfo", "r");

    if (!f) return 0;
    while (fgets(line, sizeof line, f))
        if (strncmp(line, key, klen) == 0 && line[klen] == ':') {
            sscanf(line + klen + 1, "%lu", &v);
            break;
        }
    fclose(f);
    return v;
}

/* «1234567» → «1 234 567». Вісім буферів по колу — стільки, скільки найбільше
   викликів трапляється в одному printf. */
static const char *sp(unsigned long v)
{
    static char ring[8][32];
    static int slot;
    char raw[24], *out = ring[slot = (slot + 1) % 8];
    int n = snprintf(raw, sizeof raw, "%lu", v), i, j = 0;

    for (i = 0; i < n; i++) {
        if (i && (n - i) % 3 == 0) out[j++] = ' ';
        out[j++] = raw[i];
    }
    out[j] = '\0';
    return out;
}

static void snapshot(const char *when, unsigned char *r[3])
{
    struct proc_ksm k;
    int i;

    printf("\n── %s ──\n", when);
    /* Колонки підписані латиницею навмисно: %-10s рівняє за БАЙТАМИ,
       а кирилична літера в UTF-8 займає два — заголовок би поїхав. */
    puts("        Rss          Pss          KSM        Swap      VmFlags");
    for (i = 0; i < 3; i++) {
        struct vma_stat v;

        smaps_of(r[i], &v);
        printf("%c %9s кБ %9s кБ %9s кБ %8s кБ   %s%s\n", "ABC"[i],
               sp(v.rss), sp(v.pss), sp(v.ksm), sp(v.swap),
               v.mergeable ? "mg " : "БЕЗ mg ", v.nohuge ? "nh" : "");
    }

    proc_ksm_read(&k);
    printf("ksm_stat: rmap_items %s  merging_pages %s  zero_pages %ld  "
           "process_profit %ld Б (%.1f МіБ)\n",
           sp(k.rmap_items), sp(k.merging_pages), k.zero_pages,
           k.profit, k.profit / 1048576.0);
    if (k.rmap_items && k.merging_pages) {
        double item = ((double)(k.merging_pages + k.zero_pages) * PAGE - k.profit)
                      / k.rmap_items;
        printf("          звідси розмір службової структури: %.1f Б "
               "на відстежувану сторінку\n", item);
    }

    printf("система : pages_shared %ld  pages_sharing %ld  pages_unshared %ld  "
           "pages_volatile %ld  full_scans %ld\n",
           ksm_get("pages_shared"), ksm_get("pages_sharing"),
           ksm_get("pages_unshared"), ksm_get("pages_volatile"),
           ksm_get("full_scans"));
    printf("MemFree : %s кБ\n", sp(meminfo("MemFree")));
}

static void wait_scans(long n)
{
    long start = ksm_get("full_scans"), now = start;
    struct timespec t0, t1, nap = { 0, 100L * 1000 * 1000 };

    clock_gettime(CLOCK_MONOTONIC, &t0);
    printf("\nчекаємо %ld повних проходів ksmd (full_scans зараз %ld)", n, start);
    fflush(stdout);

    while (now - start < n) {
        nanosleep(&nap, NULL);
        if ((now = ksm_get("full_scans")) < 0) { puts(" — ksmd зник?"); return; }
        putchar('.');
        fflush(stdout);
    }
    clock_gettime(CLOCK_MONOTONIC, &t1);
    printf(" готово за %.1f с\n",
           (t1.tv_sec - t0.tv_sec) + (t1.tv_nsec - t0.tv_nsec) / 1e9);
}
