/* Знаходимо ділянку, що містить addr, і беремо з неї два числа. */
static void vma_pages(const void *addr, long *anon_kb, long *page_kb)
{
        FILE *f = fopen("/proc/self/smaps", "r");
        char line[512], perms[8];
        unsigned long lo, hi;
        int inside = 0;

        *anon_kb = *page_kb = -1;
        if (!f)
                return;
        while (fgets(line, sizeof line, f)) {
                if (sscanf(line, "%lx-%lx %7s", &lo, &hi, perms) == 3) {
                        inside = ((uintptr_t)addr >= lo && (uintptr_t)addr < hi);
                        continue;               /* заголовок ділянки */
                }
                if (!inside)
                        continue;
                if (!strncmp(line, "AnonHugePages:", 14))
                        sscanf(line + 14, "%ld", anon_kb);
                else if (!strncmp(line, "KernelPageSize:", 15))
                        sscanf(line + 15, "%ld", page_kb);
        }
        fclose(f);
}

/* Скільки разів ядро хотіло велику сторінку й не знайшло суцільного блоку. */
static unsigned long vmstat(const char *key)
{
        FILE *f = fopen("/proc/vmstat", "r");
        char name[64];
        unsigned long v, out = 0;

        if (!f)
                return 0;
        while (fscanf(f, "%63s %lu", name, &v) == 2)
                if (!strcmp(name, key)) { out = v; break; }
        fclose(f);
        return out;
}
