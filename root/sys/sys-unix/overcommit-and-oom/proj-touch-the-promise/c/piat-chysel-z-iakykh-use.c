static char cgdir[512];                    /* порожньо — стелі групи нема */

static void cg_find(void)
{
    FILE *f = fopen("/proc/self/cgroup", "re");
    if (!f) return;
    char line[448];
    while (fgets(line, sizeof line, f))
        if (!strncmp(line, "0::", 3)) {                 /* «0::» — це cgroup v2 */
            line[strcspn(line, "\n")] = '\0';
            snprintf(cgdir, sizeof cgdir, "/sys/fs/cgroup%s", line + 3);
            break;
        }
    fclose(f);
}

/* Перше число з файла групи. -1, якщо файла нема або там слово «max». */
static long cg_num(const char *file)
{
    if (!cgdir[0]) return -1;
    char path[640];
    snprintf(path, sizeof path, "%s/%s", cgdir, file);
    FILE *f = fopen(path, "re");
    if (!f) return -1;
    long v;
    if (fscanf(f, "%ld", &v) != 1) v = -1;
    fclose(f);
    return v;
}

/* Лічильник із memory.events — рядки вигляду «ключ ЧИСЛО».
   Пробіл після ключа обов'язковий: інакше «oom» злапає «oom_kill». */
static long cg_event(const char *key)
{
    if (!cgdir[0]) return -1;
    char path[640], line[128];
    snprintf(path, sizeof path, "%s/memory.events", cgdir);
    FILE *f = fopen(path, "re");
    if (!f) return -1;
    const size_t klen = strlen(key);
    long v = -1;
    while (fgets(line, sizeof line, f))
        if (!strncmp(line, key, klen) && line[klen] == ' ') {
            v = strtol(line + klen + 1, NULL, 10);
            break;
        }
    fclose(f);
    return v;
}

static void cg_show(void)
{
    long max = cg_num("memory.max");       /* слово «max» → -1: стелі нема */
    if (max < 0) return;
    printf("  ||%8.1f/%.0f МіБ  впер=%ld oom=%ld",
           cg_num("memory.current") / (double) MIB, max / (double) MIB,
           cg_event("max"), cg_event("oom"));
}

/* Один рядок стану. Підпис стоїть ОСТАННІМ навмисно: printf рівняє поля
   за байтами, а не за знаками, і кирилиця в «%-16s» зсунула б колонки. */
static void snap(const char *tag)
{
    printf("%9.1f %9.1f %9.1f  ||%11.1f %11.1f",
           field_kb("/proc/self/status", "VmSize")     / 1024.0,
           field_kb("/proc/self/status", "VmRSS")      / 1024.0,
           field_kb("/proc/self/status", "VmSwap")     / 1024.0,
           field_kb("/proc/meminfo",     "Committed_AS") / 1024.0,
           field_kb("/proc/meminfo",     "MemAvailable") / 1024.0);
    cg_show();
    printf("   %s\n", tag);
}
