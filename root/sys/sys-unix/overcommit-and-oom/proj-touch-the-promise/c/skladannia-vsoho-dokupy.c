int main(int argc, char **argv)
{
    setvbuf(stdout, NULL, _IOLBF, 0);
    pgsz = (size_t) sysconf(_SC_PAGESIZE);

    if (argc < 2) { fprintf(stderr, "режим: reserve | touch | wall\n"); return 2; }
    const char *mode = argv[1];

    size_t size = 8 * GIB, step = 256 * MIB, limit_as = 0;
    unsigned pause_ms = 0;
    enum how how = H_MALLOC;
    int read_only = 0, release = 0, adj = 0, has_adj = 0;

    for (int i = 2; i < argc; i++) {
        const char *a = argv[i];
        int more = i + 1 < argc;
        if      (!strcmp(a, "--size")     && more) size     = (size_t)(atof(argv[++i]) * GIB);
        else if (!strcmp(a, "--step")     && more) step     = (size_t)(atof(argv[++i]) * MIB);
        else if (!strcmp(a, "--pause")    && more) pause_ms = (unsigned) atoi(argv[++i]);
        else if (!strcmp(a, "--limit-as") && more) limit_as = (size_t)(atof(argv[++i]) * GIB);
        else if (!strcmp(a, "--adj")      && more) { adj = atoi(argv[++i]); has_adj = 1; }
        else if (!strcmp(a, "--noreserve")) how = H_NORESERVE;
        else if (!strcmp(a, "--calloc"))    how = H_CALLOC;
        else if (!strcmp(a, "--read"))      read_only = 1;
        else if (!strcmp(a, "--release"))   release   = 1;
        else { fprintf(stderr, "не знаю опції %s\n", a); return 2; }
    }
    if (step < pgsz) step = pgsz;

    cg_find();
    if (has_adj)  set_adj(adj);
    if (limit_as) set_limit_as(limit_as);   /* ліміт — ДО обіцянки, інакше марно */

    printf("сторінка %zu Б, обіцянка %.2f ГіБ, крок %.2f МіБ\n",
           pgsz, size / (double) GIB, step / (double) MIB);
    printf("%9s %9s %9s  ||%11s %11s   %s\n",
           "VmSize", "VmRSS", "VmSwap", "Committed", "MemAvail", "подія");
    snap("до обіцянки");

    void *p = promise(size, how);
    if (!p) return 1;
    snap("після обіцянки");

    if (!strcmp(mode, "reserve")) return 0;
    if (strcmp(mode, "touch") && strcmp(mode, "wall")) {
        fprintf(stderr, "невідомий режим %s\n", mode);
        return 2;
    }
    touch(p, size, step, strcmp(mode, "wall") ? pause_ms : 0, read_only, release);
    snap("кінець");
    return 0;
}
