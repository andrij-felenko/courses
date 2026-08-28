/* spawncost.c — три способи народити процес на одних терезах. */
#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <spawn.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <sys/resource.h>
#include <sys/wait.h>
#include <time.h>
#include <unistd.h>

extern char **environ;

/* HELPER — масив, а не покажчик: тоді його ім'я є сталим адресним виразом
   і ним можна ініціалізувати статичний ARGV. А ARGV має бути готовий ДО
   виклику vfork: у дитині вже нічого не можна побудувати. */
static char  HELPER[] = "./noop";
static char *ARGV[]   = { HELPER, NULL };

static struct timespec now(void)
{
    struct timespec t;
    clock_gettime(CLOCK_MONOTONIC, &t);
    return t;
}

/* Різниця двох моментів у мілісекундах. Віднімаємо ЦІЛІ поля й лише потім
   переводимо в double: секунди від старту системи, помножені на 10⁹, з'їли б
   усю точність мантиси, і наносекунди в ній потонули б. */
static double ms_between(struct timespec a, struct timespec b)
{
    return (double)(b.tv_sec - a.tv_sec) * 1e3
         + (double)(b.tv_nsec - a.tv_nsec) / 1e6;
}

/* Одне поле з файлу /proc, у кілобайтах; −1, якщо поля немає. */
static long field_kb(const char *path, const char *key)   /* key — «VmPTE:» */
{
    static char buf[8192];
    char pat[64];

    int fd = open(path, O_RDONLY);
    if (fd < 0)
        return -1;
    buf[0] = '\n';                       /* щоб шукати саме початок РЯДКА */
    ssize_t n = read(fd, buf + 1, sizeof(buf) - 2);
    close(fd);
    if (n <= 0)
        return -1;
    buf[n + 1] = '\0';

    snprintf(pat, sizeof(pat), "\n%s", key);
    char *s = strstr(buf, pat);
    return s ? strtol(s + strlen(pat), NULL, 10) : -1;
}

/* Пам'ять батька: рівно стільки ТОРКНУТИХ сторінок, скільки просили. */
static void grow_parent(size_t bytes, int huge)
{
    if (bytes == 0)
        return;
    char *p = mmap(NULL, bytes, PROT_READ | PROT_WRITE,
                   MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if (p == MAP_FAILED) {
        perror("mmap");
        exit(1);
    }
    /* Кажемо явно в ОБИДВА боки: інакше результат залежатиме від того, як
       великі сторінки налаштовані в цій системі, і два запуски на різних
       машинах виявляться незіставними. */
    madvise(p, bytes, huge ? MADV_HUGEPAGE : MADV_NOHUGEPAGE);

    size_t page = (size_t)sysconf(_SC_PAGESIZE);
    for (size_t off = 0; off < bytes; off += page)
        p[off] = 1;                      /* без дотику статей таблиць не буде */
}

static pid_t spawn_fork(void)
{
    pid_t pid = fork();
    if (pid < 0) {
        perror("fork");
        exit(1);
    }
    if (pid == 0) {
        execv(HELPER, ARGV);
        _exit(127);
    }
    return pid;
}

/* vfork: дитина живе в пам'яті батька, тож їй дозволено рівно два кроки —
   exec або _exit. Ні printf (це буфери батька), ні exit (це його обробники
   atexit), ні виходу з цієї функції (це рамка стека, у яку батько
   повернеться). Навіть повідомлення про помилку — тільки write(2), і рядок
   до нього лежить у сталих даних, а не на стеку. */
static pid_t spawn_vfork(void)
{
    static const char msg[] = "execv failed\n";
    pid_t pid = vfork();
    if (pid < 0) {
        perror("vfork");
        exit(1);
    }
    if (pid == 0) {
        execv(HELPER, ARGV);
        (void)!write(STDERR_FILENO, msg, sizeof msg - 1);
        _exit(127);
    }
    return pid;
}

/* posix_spawn повертає код помилки ЗНАЧЕННЯМ і не чіпає errno — тому тут
   strerror(rc), а не perror(). */
static pid_t spawn_posix(void)
{
    pid_t pid;
    int rc = posix_spawn(&pid, HELPER, NULL, NULL, ARGV, environ);
    if (rc != 0) {
        fprintf(stderr, "posix_spawn: %s\n", strerror(rc));
        exit(1);
    }
    return pid;
}

static int cmp_double(const void *a, const void *b)
{
    double x = *(const double *)a, y = *(const double *)b;
    return (x > y) - (x < y);
}

static void reap(pid_t pid)
{
    int st;
    while (waitpid(pid, &st, 0) < 0 && errno == EINTR)
        ;
}

static void run(const char *name, pid_t (*spawn)(void), int iters, double *v)
{
    struct rusage r0, r1;

    reap(spawn());                       /* прогрів: помічник у кеші сторінок */

    getrusage(RUSAGE_SELF, &r0);
    struct timespec t0 = now();
    for (int i = 0; i < iters; i++) {
        struct timespec c0 = now();
        pid_t pid = spawn();
        struct timespec c1 = now();
        v[i] = ms_between(c0, c1);
        reap(pid);
    }
    struct timespec t1 = now();
    getrusage(RUSAGE_SELF, &r1);

    double whole = ms_between(t0, t1) / iters;
    double sys   = ((double)(r1.ru_stime.tv_sec  - r0.ru_stime.tv_sec) * 1e3
                  + (double)(r1.ru_stime.tv_usec - r0.ru_stime.tv_usec) / 1e3)
                 / iters;

    /* Медіана, а не середнє: один запуск, якому не пощастило з планувальником
       чи з частотою ядра, здатен зіпсувати середнє на десятки відсотків. */
    qsort(v, (size_t)iters, sizeof v[0], cmp_double);
    printf("%-12s %9.3f %11.3f %10.3f\n", name, v[iters / 2], sys, whole);
}

int main(int argc, char **argv)
{
    size_t mib   = (argc > 1) ? strtoul(argv[1], NULL, 10) : 1024;
    int    iters = (argc > 2) ? atoi(argv[2]) : 200;
    int    huge  = (argc > 3 && strcmp(argv[3], "--huge") == 0);

    if (iters < 3)
        iters = 3;
    grow_parent(mib << 20, huge);

    printf("батько: %zu МіБ торкнутих · VmRSS %ld КіБ · VmPTE %ld КіБ"
           " · великі сторінки %ld КіБ\n",
           mib,
           field_kb("/proc/self/status", "VmRSS:"),
           field_kb("/proc/self/status", "VmPTE:"),
           field_kb("/proc/self/smaps_rollup", "AnonHugePages:"));
    puts("спосіб       у виклику  sys батька     усього");

    double *v = malloc(sizeof *v * (size_t)iters);
    if (!v)
        return 1;
    run("fork+exec",   spawn_fork,  iters, v);
    run("vfork+exec",  spawn_vfork, iters, v);
    run("posix_spawn", spawn_posix, iters, v);
    free(v);
    return 0;
}
