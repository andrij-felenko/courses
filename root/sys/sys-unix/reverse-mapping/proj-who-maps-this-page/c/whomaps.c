/* whomaps.c — за номером фізичного кадру знайти всі його відображення в системі.
 *
 *   cc -O2 -Wall -Wextra -o whomaps whomaps.c
 *   sudo ./whomaps 0x11e347              — шукати кадр за номером
 *   sudo ./whomaps 1234@0x7f2a4c014000   — спершу перекласти адресу процесу в кадр
 */
#define _GNU_SOURCE
#define _FILE_OFFSET_BITS 64      /* зміщення в pagemap легко перевалює за 2 ГіБ */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <inttypes.h>
#include <ctype.h>
#include <unistd.h>
#include <fcntl.h>
#include <dirent.h>

#define PAGE_SZ 4096ULL
#define ENTRY   8ULL              /* один запис pagemap — рівно 8 байтів */
#define CHUNK   1024              /* скільки записів беремо за одне читання */

#define PM_PRESENT   (1ULL << 63)
#define PM_EXCLUSIVE (1ULL << 56)
#define PM_PFN_MASK  ((1ULL << 55) - 1)

#define KPF_ANON (1ULL << 12)
#define KPF_KSM  (1ULL << 21)
#define KPF_THP  (1ULL << 22)

static uint64_t      target;      /* шуканий номер кадру */
static unsigned long found;       /* скільки відображень знайшли */

/* Прочитати 8 байтів із файлу, індексованого номером кадру. */
static int kpage_u64(const char *path, uint64_t pfn, uint64_t *out)
{
    int fd = open(path, O_RDONLY);
    if (fd < 0) return -1;
    ssize_t got = pread(fd, out, ENTRY, (off_t)(pfn * ENTRY));
    close(fd);
    return got == (ssize_t)ENTRY ? 0 : -1;
}

/* Пройти одну ділянку [start, end) блоками по CHUNK записів. */
static void scan_range(int pmfd, int pid, const char *comm,
                       uint64_t start, uint64_t end, const char *label)
{
    static uint64_t buf[CHUNK];

    for (uint64_t va = start; va < end; ) {
        uint64_t left = (end - va) / PAGE_SZ;
        size_t   n    = left > CHUNK ? CHUNK : (size_t)left;

        ssize_t got = pread(pmfd, buf, n * ENTRY, (off_t)(va / PAGE_SZ * ENTRY));
        if (got <= 0) return;                 /* процес зник або ділянка недосяжна */

        size_t k = (size_t)got / ENTRY;
        for (size_t i = 0; i < k; i++) {
            uint64_t e = buf[i];
            if (!(e & PM_PRESENT))            continue;   /* дірка або своп */
            if ((e & PM_PFN_MASK) != target)  continue;

            printf("  pid %-7d %-16s %#018" PRIx64 "  %s%s\n",
                   pid, comm, va + (uint64_t)i * PAGE_SZ, label,
                   (e & PM_EXCLUSIVE) ? "   [єдине відображення]" : "");
            found++;
        }
        va += (uint64_t)k * PAGE_SZ;
    }
}

/* Прочитати maps одного процесу й пройти кожну його ділянку. */
static void scan_pid(int pid)
{
    char path[64], line[512], comm[32] = "?";

    snprintf(path, sizeof path, "/proc/%d/maps", pid);
    FILE *maps = fopen(path, "r");
    if (!maps) return;                        /* процес щойно помер — це нормально */

    snprintf(path, sizeof path, "/proc/%d/pagemap", pid);
    int pmfd = open(path, O_RDONLY);
    if (pmfd < 0) { fclose(maps); return; }

    snprintf(path, sizeof path, "/proc/%d/comm", pid);
    FILE *c = fopen(path, "r");
    if (c) {
        if (fgets(comm, sizeof comm, c)) comm[strcspn(comm, "\n")] = '\0';
        fclose(c);
    }

    while (fgets(line, sizeof line, maps)) {
        char    *p     = line;
        uint64_t start = strtoull(p, &p, 16);
        if (*p != '-') continue;
        uint64_t end   = strtoull(p + 1, &p, 16);

        /* Пропускаємо чотири поля: права, зміщення, пристрій, інод. */
        for (int f = 0; f < 4; f++) {
            while (*p == ' ') p++;
            while (*p && *p != ' ' && *p != '\n') p++;
        }
        while (*p == ' ') p++;
        p[strcspn(p, "\n")] = '\0';

        const char *label = *p ? p : "[анонімна]";
        if (!strcmp(label, "[vsyscall]")) continue;   /* не звичайна пам'ять */

        scan_range(pmfd, pid, comm, start, end, label);
    }

    close(pmfd);
    fclose(maps);
}

int main(int argc, char **argv)
{
    if (argc != 2) {
        fprintf(stderr, "вжиток: %s <кадр> | <pid>@<адреса>\n", argv[0]);
        return 2;
    }

    char *at = strchr(argv[1], '@');
    if (at) {                                  /* адреса процесу → номер кадру */
        *at = '\0';
        char path[64];
        uint64_t va = strtoull(at + 1, NULL, 0), e = 0;

        snprintf(path, sizeof path, "/proc/%s/pagemap", argv[1]);
        int fd = open(path, O_RDONLY);
        if (fd < 0 || pread(fd, &e, ENTRY, (off_t)(va / PAGE_SZ * ENTRY)) != (ssize_t)ENTRY) {
            perror("pagemap");
            return 1;
        }
        close(fd);
        if (!(e & PM_PRESENT)) {
            fprintf(stderr, "за цією адресою зараз немає кадру (біт 63 = 0)\n");
            return 1;
        }
        target = e & PM_PFN_MASK;
    } else {
        target = strtoull(argv[1], NULL, 0);
    }

    if (target == 0) {
        fprintf(stderr, "кадр 0: найпевніше бракує CAP_SYS_ADMIN — "
                        "ядро обнулює поле номера кадру\n");
        return 1;
    }

    uint64_t count = 0, flags = 0;
    int have_count = kpage_u64("/proc/kpagecount", target, &count) == 0;
    int have_flags = kpage_u64("/proc/kpageflags", target, &flags) == 0;

    printf("кадр %#" PRIx64 "  (фізична адреса %#" PRIx64 ")\n",
           target, target * PAGE_SZ);
    if (have_flags)
        printf("прапорці %#" PRIx64 "%s%s%s\n", flags,
               (flags & KPF_ANON) ? "  ANON" : "",
               (flags & KPF_KSM)  ? "  KSM"  : "",
               (flags & KPF_THP)  ? "  THP"  : "");
    if (have_count)
        printf("ядро налічує відображень: %" PRIu64 "\n", count);
    puts("знайдено:");

    DIR *proc = opendir("/proc");
    if (!proc) { perror("/proc"); return 1; }

    struct dirent *d;
    while ((d = readdir(proc)))
        if (isdigit((unsigned char)d->d_name[0]))
            scan_pid((int)strtol(d->d_name, NULL, 10));
    closedir(proc);

    printf("разом %lu", found);
    if (have_count) printf(", ядро каже %" PRIu64, count);
    putchar('\n');
    return 0;
}
