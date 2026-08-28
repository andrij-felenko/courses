/* forkcost.c — дві статті витрат fork, які видно на власній машині. */
#define _GNU_SOURCE
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <sys/resource.h>
#include <sys/wait.h>
#include <time.h>
#include <unistd.h>

static size_t PAGE;              /* розмір сторінки цієї машини */

/* Різниця двох моментів у мілісекундах. Віднімаємо ЦІЛІ поля й лише потім
   переводимо в double: секунди від старту системи, помножені на 10⁶, з'їли б
   усю точність мантиси, і наносекунди в ній потонули б. */
static double ms_between(struct timespec a, struct timespec b)
{
    return (double)(b.tv_sec - a.tv_sec) * 1e3
         + (double)(b.tv_nsec - a.tv_nsec) / 1e6;
}

/* Одне поле з /proc/self/smaps_rollup, у кілобайтах; −1, якщо поля нема.
   Файл малий і віддається одним читанням, тож stdio тут зайве: воно саме
   виділило б буфер і додало винятків рівно туди, де ми їх рахуємо. */
static long rollup(const char *key)          /* key — напр. "Private_Dirty:" */
{
    static char buf[8192];
    char pat[64];

    int fd = open("/proc/self/smaps_rollup", O_RDONLY);
    if (fd < 0)
        return -1;
    buf[0] = '\n';                           /* щоб шукати початок РЯДКА */
    ssize_t n = read(fd, buf + 1, sizeof(buf) - 2);
    close(fd);
    if (n <= 0)
        return -1;
    buf[n + 1] = '\0';

    snprintf(pat, sizeof(pat), "\n%s", key); /* «\nPss:» не збіжиться з «Pss_Anon:» */
    char *s = strstr(buf, pat);
    return s ? strtol(s + strlen(pat), NULL, 10) : -1;
}

/* Ділянка потрібного обсягу; touch=1 — записати по байту в кожну сторінку. */
static void *area(size_t bytes, int touch, int allow_thp)
{
    void *p = mmap(NULL, bytes, PROT_READ | PROT_WRITE,
                   MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if (p == MAP_FAILED) {
        perror("mmap");
        exit(1);
    }
    if (!allow_thp)                          /* ДО дотику, інакше вже пізно */
        (void)madvise(p, bytes, MADV_NOHUGEPAGE);
    if (touch) {
        volatile unsigned char *q = p;       /* volatile — щоб не викинув компілятор */
        for (size_t off = 0; off < bytes; off += PAGE)
            q[off] = 1;
    }
    return p;
}

/* ── Частина 1: затримка fork ─────────────────────────────────────────────── */

/* Час, за який fork повертається В БАТЬКА. Дитина не робить нічого. */
static double fork_once(void)
{
    struct timespec t0, t1;

    clock_gettime(CLOCK_MONOTONIC, &t0);
    pid_t pid = fork();
    if (pid == 0)
        _exit(0);                            /* НЕ exit: ні atexit, ні буферів */
    clock_gettime(CLOCK_MONOTONIC, &t1);
    if (pid < 0) {
        perror("fork");
        exit(1);
    }
    waitpid(pid, NULL, 0);
    return ms_between(t0, t1);
}

static void part1(size_t max_mib, int reps, int touch, int allow_thp)
{
    double prev_ms = 0.0;
    size_t prev_mib = 0;

    printf("  МіБ   таблиці, КіБ    fork, мс   нахил, мс/ГіБ\n");
    for (size_t mib = 64; mib <= max_mib; mib *= 2) {
        size_t bytes = mib << 20;
        void *p = area(bytes, touch, allow_thp);

        double best = 1e9;                   /* мінімум, а не середнє: шум лише додає */
        for (int i = 0; i < reps; i++) {
            double d = fork_once();
            if (d < best)
                best = d;
        }
        munmap(p, bytes);

        char slope[32];
        if (prev_mib)
            snprintf(slope, sizeof(slope), "%.2f",
                     (best - prev_ms) * 1024.0 / (double)(mib - prev_mib));
        else
            snprintf(slope, sizeof(slope), "%s", "—");
        printf("%5zu   %12zu   %9.3f   %12s\n",
               mib, bytes / PAGE * 8 / 1024, best, slope);

        prev_ms = best;
        prev_mib = mib;
    }
}

/* ── Частина 2: скільки сторінок справді скопійовано ──────────────────────── */

static void part2(size_t mib, size_t touch_mib, int keep_child, int allow_thp)
{
    size_t bytes = mib << 20;
    void *p = area(bytes, 1, allow_thp);
    int sync_pipe[2];
    struct rusage r0, r1;

    if (pipe(sync_pipe) < 0) {
        perror("pipe");
        exit(1);
    }

    /* Прогрів: перший похід у /proc сам коштує кількох винятків. Хай вони
       трапляться ДО того, як почнемо рахувати. */
    rollup("Rss:");
    getrusage(RUSAGE_SELF, &r0);

    pid_t pid = fork();
    if (pid < 0) {
        perror("fork");
        exit(1);
    }
    if (pid == 0) {
        close(sync_pipe[1]);
        char c;
        ssize_t n = read(sync_pipe[0], &c, 1); /* спить, доки батько пише */
        (void)n;
        _exit(0);
    }
    close(sync_pipe[0]);

    if (!keep_child) {                       /* варіант «дитина вже мертва» */
        close(sync_pipe[1]);
        waitpid(pid, NULL, 0);
    }

    long thp  = rollup("AnonHugePages:");
    long rss0 = rollup("Rss:"),           pss0 = rollup("Pss:");
    long pd0  = rollup("Private_Dirty:"), sd0  = rollup("Shared_Dirty:");
    getrusage(RUSAGE_SELF, &r0);             /* оце вже справжня основа виміру */

    size_t pages = (touch_mib << 20) / PAGE;
    volatile unsigned char *q = p;
    for (size_t i = 0; i < pages; i++)
        q[i * PAGE] += 1;                    /* читання-запис: виняток гарантовано */

    getrusage(RUSAGE_SELF, &r1);
    long rss1 = rollup("Rss:"),           pss1 = rollup("Pss:");
    long pd1  = rollup("Private_Dirty:"), sd1  = rollup("Shared_Dirty:");

    printf("  ділянка               : %zu МіБ, сторінка %zu Б%s\n", mib, PAGE,
           keep_child ? "" : "   [дитина вже завершилась]");
    printf("  AnonHugePages         : %ld КіБ%s\n", thp,
           thp > 0 ? "   ⚠ великі сторінки живі" : "");
    printf("  зачеплено сторінок    : %zu  (%zu МіБ)\n", pages, touch_mib);
    printf("  ru_minflt приріст     : %ld\n", r1.ru_minflt - r0.ru_minflt);
    printf("  Private_Dirty         : %ld → %ld КіБ  (%+ld)\n", pd0, pd1, pd1 - pd0);
    printf("  Shared_Dirty          : %ld → %ld КіБ  (%+ld)\n", sd0, sd1, sd1 - sd0);
    printf("  Pss                   : %ld → %ld КіБ  (%+ld)\n", pss0, pss1, pss1 - pss0);
    printf("  Rss                   : %ld → %ld КіБ  (%+ld)\n", rss0, rss1, rss1 - rss0);
    printf("  скопійовано сторінок  : %ld  (з приросту Private_Dirty)\n",
           (pd1 - pd0) * 1024 / (long)PAGE);

    if (keep_child) {
        close(sync_pipe[1]);                 /* дитина прокидається й виходить */
        waitpid(pid, NULL, 0);
    }
    munmap(p, bytes);
}

int main(int argc, char **argv)
{
    PAGE = (size_t)sysconf(_SC_PAGESIZE);
    const char *mode = argc > 1 ? argv[1] : "lat";
    size_t a = argc > 2 ? strtoul(argv[2], NULL, 10) : 0;
    size_t b = argc > 3 ? strtoul(argv[3], NULL, 10) : 0;

    if (!strcmp(mode, "lat"))            part1(a ? a : 2048, 7, 1, 0);
    else if (!strcmp(mode, "lat-cold"))  part1(a ? a : 2048, 7, 0, 0);
    else if (!strcmp(mode, "lat-thp"))   part1(a ? a : 2048, 7, 1, 1);
    else if (!strcmp(mode, "cow"))       part2(a ? a : 512, b ? b : 64, 1, 0);
    else if (!strcmp(mode, "cow-dead"))  part2(a ? a : 512, b ? b : 64, 0, 0);
    else {
        fprintf(stderr, "режими: lat | lat-cold | lat-thp | cow | cow-dead\n");
        return 2;
    }
    return 0;
}
