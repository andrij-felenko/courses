/* PSS процесу одним числом. −1 — не прочитали, 0 — процес без карти. */
static long rollup_pss(long pid)
{
    char path[64];
    snprintf(path, sizeof path, "/proc/%ld/smaps_rollup", pid);

    size_t len;
    char *buf = slurp(path, &len);
    if (!buf)
        return -1;

    long pss = 0;
    for (char *p = buf; p && *p; ) {
        if (strncmp(p, "Pss:", 4) == 0) {    /* саме "Pss:", не "Pss_Anon:" */
            pss = strtol(p + 4, NULL, 10);
            break;
        }
        p = strchr(p, '\n');
        if (p) p++;
    }
    free(buf);
    return pss;
}

static unsigned long meminfo(const char *key)
{
    size_t len, klen = strlen(key);
    char *buf = slurp("/proc/meminfo", &len);
    if (!buf)
        return 0;

    unsigned long v = 0;
    for (char *p = buf; p && *p; ) {
        if (strncmp(p, key, klen) == 0 && p[klen] == ':') {
            v = strtoul(p + klen + 1, NULL, 10);
            break;
        }
        p = strchr(p, '\n');
        if (p) p++;
    }
    free(buf);
    return v;
}

static void scan_all(void)
{
    DIR *d = opendir("/proc");
    if (!d) { perror("/proc"); return; }

    unsigned long sum = 0;
    unsigned counted = 0, nomm = 0, denied = 0;

    for (struct dirent *e; (e = readdir(d)); ) {
        if (e->d_name[0] < '1' || e->d_name[0] > '9')
            continue;                        /* "self", "meminfo", "." — не pid */

        long pss = rollup_pss(strtol(e->d_name, NULL, 10));
        if (pss < 0)       denied++;         /* ENOENT, ESRCH, EACCES */
        else if (pss == 0) nomm++;           /* ядрова нитка */
        else { sum += (unsigned long)pss; counted++; }
    }
    closedir(d);

    unsigned long expect = meminfo("AnonPages") + meminfo("Mapped");
    printf("пораховано процесів  %8u   (ядрових ниток %u, недоступних %u)\n",
           counted, nomm, denied);
    printf("Σ PSS                %8lu кБ\n", sum);
    printf("AnonPages + Mapped   %8lu кБ\n", expect);
    printf("розбіжність          %11.2f %%\n",
           expect ? 100.0 * ((double)sum - (double)expect) / (double)expect : 0.0);
}

int main(int argc, char **argv)
{
    if (argc == 2 && strcmp(argv[1], "-a") == 0) { scan_all(); return 0; }
    if (argc >= 2) {
        report_pid(strtol(argv[1], NULL, 10),
                   argc > 2 ? (int)strtol(argv[2], NULL, 10) : 12);
        return 0;
    }
    fprintf(stderr, "вжиток: pssmap <pid> [рядків] | pssmap -a\n");
    return 2;
}
