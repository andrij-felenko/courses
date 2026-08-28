/* report.c — новий образ: що з виставленого стендом дожило до цієї миті.
   Збірка: cc -O2 -Wall -Wextra -o report report.c                     */
#define _GNU_SOURCE
#include <dirent.h>
#include <errno.h>
#include <fcntl.h>
#include <limits.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/resource.h>
#include <sys/stat.h>
#include <sys/syscall.h>
#include <sys/time.h>
#include <time.h>
#include <unistd.h>

static int mismatch = 0;

static const char *want(const char *name)
{
    const char *v = getenv(name);
    if (v == NULL) {
        fprintf(stderr, "звітувача запускає стенд, а не оболонка: немає %s\n", name);
        exit(2);
    }
    return v;
}

/* present — чи є воно в новому образі; expected — чи мало бути */
static void check(int present, int expected, const char *what, const char *detail)
{
    if (present != expected) mismatch++;
    printf("  %c%c  %s%s%s\n", present ? '+' : '-',
           present == expected ? ' ' : '!',
           what, *detail ? " — " : "", detail);
}

static int addr_is_mapped(unsigned long long a)
{
    unsigned long long lo, hi;
    char row[512];
    int found = 0;
    FILE *f = fopen("/proc/self/maps", "r");
    if (f == NULL) return -1;
    while (fgets(row, sizeof row, f))
        if (sscanf(row, "%llx-%llx", &lo, &hi) == 2 && a >= lo && a < hi) {
            found = 1;
            break;
        }
    fclose(f);
    return found;
}

static void list_open_fds(void)
{
    struct dirent *e;
    DIR *d = opendir("/proc/self/fd");
    int self;
    if (d == NULL) { printf("     (/proc не змонтовано)\n"); return; }
    self = dirfd(d);          /* власний дескриптор каталогу до переліку не належить */
    while ((e = readdir(d)) != NULL) {
        char path[64], target[PATH_MAX];
        ssize_t n;
        int fd = atoi(e->d_name);
        if (e->d_name[0] == '.' || fd == self) continue;
        snprintf(path, sizeof path, "/proc/self/fd/%d", fd);
        n = readlink(path, target, sizeof target - 1);
        if (n < 0) continue;
        target[n] = '\0';
        printf("     fd %d → %s\n", fd, target);
    }
    closedir(d);
}

int main(int argc, char **argv)
{
    int keep       = atoi(want("SURV_FD"));
    int cloexec    = atoi(want("SURV_FD_CLOEXEC"));
    int ktimer     = atoi(want("SURV_TIMER"));
    long was_pid   = atol(want("SURV_PID"));
    double was_cpu = atof(want("SURV_CPU"));
    unsigned long long addr = strtoull(want("SURV_ADDR"), NULL, 0);
    unsigned long long was_nofile = strtoull(want("SURV_NOFILE"), NULL, 10);

    char detail[256], cwd[PATH_MAX];
    struct sigaction sa;
    struct itimerval it;
    struct itimerspec ts;
    struct timespec cpu;
    struct rlimit rl;
    sigset_t set;
    off_t off;
    mode_t um;
    int cl_alive, mapped, prio;
    long r;
    double now;

    (void) argc;
    printf("[звітувач] pid %ld, argv[0] = «%s»\n", (long) getpid(), argv[0]);
    printf("позначки: «+» є в новому образі, «-» немає; «!» — не збіглося\n\n");

    snprintf(detail, sizeof detail, "у стенді був %ld, зараз %ld",
             was_pid, (long) getpid());
    check(getpid() == was_pid, 1, "той самий номер процесу", detail);

    printf("\n  відкриті дескриптори нового образу:\n");
    list_open_fds();
    printf("\n");

    off = lseek(keep, 0, SEEK_CUR);
    snprintf(detail, sizeof detail, "fd %d, зсув %lld (стенд лишив 10)",
             keep, (long long) off);
    check(off >= 0, 1, "дескриптор без FD_CLOEXEC", detail);

    cl_alive = (fcntl(cloexec, F_GETFD) != -1);
    snprintf(detail, sizeof detail, "fd %d: fcntl → %s", cloexec,
             cl_alive ? "відкритий" : strerror(errno));
    check(cl_alive, 0, "дескриптор з O_CLOEXEC", detail);

    sigprocmask(SIG_BLOCK, NULL, &set);
    check(sigismember(&set, SIGUSR2), 1, "SIGUSR2 у масці заблокованих", "");

    sigpending(&set);
    check(sigismember(&set, SIGUSR2), 1, "відкладений SIGUSR2",
          "надісланий ще старій програмі");

    sigaction(SIGUSR1, NULL, &sa);
    check(sa.sa_handler != SIG_DFL, 0, "обробник SIGUSR1",
          "був адресою в старому образі");

    sigaction(SIGTERM, NULL, &sa);
    check(sa.sa_handler == SIG_IGN, 1, "ігнорування SIGTERM",
          "не адреса, а позначка");

    getitimer(ITIMER_REAL, &it);
    snprintf(detail, sizeof detail, "лишилося %ld.%03ld с із 300",
             (long) it.it_value.tv_sec, (long) it.it_value.tv_usec / 1000);
    check(it.it_value.tv_sec != 0 || it.it_value.tv_usec != 0, 1,
          "alarm(300), він же ITIMER_REAL", detail);

    errno = 0;
    r = syscall(SYS_timer_gettime, ktimer, &ts);
    snprintf(detail, sizeof detail, "ідентифікатор %d: timer_gettime → %s",
             ktimer, r == 0 ? "живий" : strerror(errno));
    check(r == 0, 0, "таймер від timer_create", detail);

    mapped = addr_is_mapped(addr);
    snprintf(detail, sizeof detail, "адреса %#llx у /proc/self/maps %s", addr,
             mapped > 0 ? "усередині відображення" : "не належить нікому");
    check(mapped > 0, 0, "сторінка mmap зі старого образу", detail);

    if (getcwd(cwd, sizeof cwd) == NULL) strcpy(cwd, "?");
    snprintf(detail, sizeof detail, "«%s»", cwd);
    check(strcmp(cwd, "/tmp") == 0, 1, "той самий поточний каталог", detail);

    um = umask(0);
    umask(um);
    snprintf(detail, sizeof detail, "%04o", (unsigned) um);
    check(um == 0027, 1, "той самий umask", detail);

    getrlimit(RLIMIT_NOFILE, &rl);
    snprintf(detail, sizeof detail, "м'який ліміт %llu",
             (unsigned long long) rl.rlim_cur);
    check(rl.rlim_cur == was_nofile, 1, "той самий RLIMIT_NOFILE", detail);

    errno = 0;
    prio = getpriority(PRIO_PROCESS, 0);
    snprintf(detail, sizeof detail, "nice = %d", prio);
    check(errno == 0 && prio == 5, 1, "те саме значення nice", detail);

    clock_gettime(CLOCK_PROCESS_CPUTIME_ID, &cpu);
    now = cpu.tv_sec + cpu.tv_nsec / 1e9;
    snprintf(detail, sizeof detail, "стенд намолов %.3f с, лічильник каже %.3f с",
             was_cpu, now);
    check(now >= was_cpu, 1, "процесорний час не скинувся", detail);

    printf("\nневідповідностей: %d\n", mismatch);
    return mismatch == 0 ? 0 : 1;
}
