/* Стовпчиків не вирівнюємо: printf рахує в %-24s байти, а не літери,
   тож на кириличному написі поле «поїде». Двокрапка чесніша за таблицю. */
static void show_file(const char *path, const char *label)
{
    char line[256];
    FILE *f = fopen(path, "r");

    if (!f) { printf("  %s: файлу немає\n", label); return; }
    if (fgets(line, sizeof line, f)) {
        line[strcspn(line, "\n")] = '\0';
        printf("  %s: %s\n", label, line);
    }
    fclose(f);
}

/* Прапорці процесора — рядок flags у /proc/cpuinfo. Шукаємо прапорець
   у пробільній рамці, щоб «pcid» не знайшовся всередині «invpcid». */
static int has_flag(const char *flag)
{
    char line[8192], needle[64];
    FILE *f = fopen("/proc/cpuinfo", "r");
    int found = 0;

    if (!f) return -1;
    snprintf(needle, sizeof needle, " %s ", flag);
    while (fgets(line, sizeof line, f)) {
        char *nl;
        if (strncmp(line, "flags", 5) != 0) continue;
        nl = strchr(line, '\n');
        if (nl) *nl = ' ';                  /* щоб рамка спрацювала й для останнього */
        found = strstr(line, needle) != NULL;
        break;
    }
    fclose(f);
    return found;
}

int main(int argc, char **argv)
{
    static const unsigned KIB[] = { 0, 64, 256, 1024, 4096, 16384, 65536, 262144 };
    static const struct { const char *name; void (*fn)(void); } PROBES[] = {
        { "clock_gettime через vDSO", probe_vdso     },
        { "clock_gettime крізь межу", probe_crossing },
        { "getppid",                  probe_getppid  },
    };
    size_t bytes = (size_t)MAX_KIB * 1024;
    int cpu = (argc > 1) ? atoi(argv[1]) : 0;
    int thp = (argc > 2 && strcmp(argv[2], "--thp") == 0);
    cpu_set_t set;
    uint8_t *buf;
    double hz;
    size_t k;

    CPU_ZERO(&set);
    CPU_SET(cpu, &set);
    if (sched_setaffinity(0, sizeof set, &set) != 0) {
        perror("sched_setaffinity");
        return 1;
    }

    buf = mmap(NULL, bytes, PROT_READ | PROT_WRITE,
               MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if (buf == MAP_FAILED) { perror("mmap"); return 1; }

    /* Прозорі великі сторінки вмикаємо або вимикаємо явно: інакше система
       підкладе 2-мебібайтні сторінки на свій розсуд — і крива тиску на TLB
       зникне сама собою, без жодного пояснення. */
    madvise(buf, bytes, thp ? MADV_HUGEPAGE : MADV_NOHUGEPAGE);
    memset(buf, 0, bytes);                  /* заселяємо сторінки наперед */

    hz = tsc_hz();

    printf("режим вимірювання\n");
    printf("  ядро процесора: %d, частота TSC: %.0f МГц\n", cpu, hz / 1e6);
    show_file("/sys/devices/system/cpu/vulnerabilities/meltdown", "meltdown");
    printf("  прапорці: pti=%d pcid=%d invpcid=%d constant_tsc=%d\n",
           has_flag("pti"), has_flag("pcid"),
           has_flag("invpcid"), has_flag("constant_tsc"));
    printf("  великі сторінки: %s\n",
           thp ? "MADV_HUGEPAGE" : "MADV_NOHUGEPAGE");

    printf("\nбез робочої множини (тактів / нс на виклик)\n");
    for (k = 0; k < sizeof PROBES / sizeof *PROBES; k++) {
        double t = cost(PROBES[k].fn, 200000, buf, 0, 5);
        printf("  %s: %.1f / %.1f\n", PROBES[k].name, t, t * 1e9 / hz);
    }

    printf("\ngetppid під тиском на TLB (тактів / нс на виклик)\n");
    for (k = 0; k < sizeof KIB / sizeof *KIB; k++) {
        size_t pages = (size_t)KIB[k] * 1024 / PAGE;
        double t;
        if (pages) chain(buf, pages);
        t = cost(probe_getppid, 20000, buf, pages, 3);
        printf("  %8u КіБ: %7.1f / %7.1f\n", KIB[k], t, t * 1e9 / hz);
    }

    munmap(buf, bytes);
    return 0;
}
