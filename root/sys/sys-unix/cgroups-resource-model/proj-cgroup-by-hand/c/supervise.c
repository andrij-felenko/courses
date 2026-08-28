/* supervise.c — запустити команду у власній cgroup і звітувати, чим вона там жила.
   збірка: cc -O2 -Wall -Wextra -o supervise supervise.c
   вжиток: ./supervise /sys/fs/cgroup/…/cglab.scope make -j16                    */

#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <limits.h>
#include <poll.h>
#include <signal.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/syscall.h>
#include <sys/wait.h>
#include <unistd.h>

#ifndef SYS_clone3
#define SYS_clone3 435              /* однаковий номер на всіх сучасних архітектурах */
#endif
#ifndef CLONE_INTO_CGROUP
#define CLONE_INTO_CGROUP 0x200000000ULL
#endif

/* struct clone_args ядра — версія з полем cgroup (Linux 5.7+) */
struct cl_args {
    uint64_t flags, pidfd, child_tid, parent_tid, exit_signal;
    uint64_t stack, stack_size, tls, set_tid, set_tid_size, cgroup;
};

static void die(const char *what) { perror(what); exit(1); }

static void put(int dir, const char *name, const char *val)
{
    int fd = openat(dir, name, O_WRONLY | O_CLOEXEC);
    if (fd < 0) die(name);
    if (write(fd, val, strlen(val)) < 0) die(name);
    close(fd);
}

static char *reread(int fd, char *buf, size_t n)          /* перечитати з початку */
{
    if (lseek(fd, 0, SEEK_SET) < 0) return NULL;
    ssize_t k = read(fd, buf, n - 1);
    if (k < 0) return NULL;
    buf[k] = '\0';
    return buf;
}

static char *slurp(int dir, const char *name, char *buf, size_t n)
{
    int fd = openat(dir, name, O_RDONLY | O_CLOEXEC);
    if (fd < 0) return NULL;
    char *r = reread(fd, buf, n);
    close(fd);
    return r;
}

/* значення ключа у файлі виду «ключ значення\n…»; -1, якщо ключа немає */
static long long key(const char *text, const char *name)
{
    size_t len = strlen(name);
    for (const char *p = text; p && *p; ) {
        if (!strncmp(p, name, len) && p[len] == ' ')
            return strtoll(p + len + 1, NULL, 10);
        p = strchr(p, '\n');
        if (p) p++;
    }
    return -1;
}

int main(int argc, char **argv)
{
    if (argc < 3) {
        fprintf(stderr, "вжиток: %s <батьківська-cgroup> <команда> [аргументи…]\n", argv[0]);
        return 2;
    }

    char path[PATH_MAX];
    snprintf(path, sizeof path, "%s/job-%d", argv[1], (int)getpid());
    if (mkdir(path, 0755) < 0) die("mkdir cgroup");

    int cg = open(path, O_RDONLY | O_DIRECTORY | O_CLOEXEC);
    if (cg < 0) die("open cgroup");

    put(cg, "memory.max",       "512M");
    put(cg, "memory.swap.max",  "0");
    put(cg, "memory.oom.group", "1");
    put(cg, "cpu.max",          "200000 100000");

    /* поріг тиску: 200 мс застою пам'яті за 2-секундне вікно.
       Дескриптор мусить лишатися відкритим — закриєш, і поріг зникне.       */
    static const char trig[] = "some 200000 2000000";
    int psi = openat(cg, "memory.pressure", O_RDWR | O_CLOEXEC);
    if (psi >= 0 && write(psi, trig, sizeof trig - 1) < 0) {
        close(psi);                      /* PSI вимкнено в ядрі — обійдемося */
        psi = -1;
    }

    /* cgroup.events треба один раз прочитати, інакше poll() не матиме
       від чого відштовхуватися: сповіщення озброюється саме читанням.       */
    int ev = openat(cg, "cgroup.events", O_RDONLY | O_CLOEXEC);
    if (ev < 0) die("cgroup.events");
    char buf[8192];
    reread(ev, buf, sizeof buf);

    struct cl_args args = {
        .flags       = CLONE_INTO_CGROUP,
        .exit_signal = SIGCHLD,
        .cgroup      = (uint64_t)cg,
    };
    long pid = syscall(SYS_clone3, &args, sizeof args);
    if (pid < 0) die("clone3");
    if (pid == 0) {                      /* перша інструкція дитини — уже в групі */
        execvp(argv[2], &argv[2]);
        _exit(127);
    }

    struct pollfd fds[2] = {
        { .fd = ev,  .events = POLLPRI, .revents = 0 },
        { .fd = psi, .events = POLLPRI, .revents = 0 },   /* -1 poll() просто ігнорує */
    };
    long stalls = 0;

    for (;;) {
        if (poll(fds, 2, -1) < 0) {
            if (errno == EINTR) continue;
            die("poll");
        }
        if (fds[1].revents & POLLPRI) {
            stalls++;
            fprintf(stderr, "[тиск] понад 200 мс застою пам'яті за останні 2 с\n");
        }
        if (fds[0].revents & POLLPRI) {
            if (!reread(ev, buf, sizeof buf)) die("cgroup.events");
            if (key(buf, "populated") == 0) break;   /* спорожніло все піддерево */
        }
    }

    int st = 0;
    while (waitpid((pid_t)pid, &st, 0) < 0)
        if (errno != EINTR) die("waitpid");

    if (slurp(cg, "cpu.stat", buf, sizeof buf))
        printf("процесор: %.3f с; періодів %lld, заморожень %lld, у заморозці %.3f с\n",
               key(buf, "usage_usec") / 1e6, key(buf, "nr_periods"),
               key(buf, "nr_throttled"), key(buf, "throttled_usec") / 1e6);

    if (slurp(cg, "memory.events", buf, sizeof buf))
        printf("пам'ять:  гальмувань %lld, упирань у стелю %lld, OOM %lld, убито %lld\n",
               key(buf, "high"), key(buf, "max"), key(buf, "oom"), key(buf, "oom_kill"));

    if (slurp(cg, "memory.peak", buf, sizeof buf))
        printf("пік:      %.1f МіБ\n", strtoll(buf, NULL, 10) / 1048576.0);

    printf("тиск:     %ld спрацювань порога\n", stalls);
    if (WIFSIGNALED(st)) printf("вихід:    сигнал %d\n", WTERMSIG(st));
    else                 printf("вихід:    код %d\n", WEXITSTATUS(st));

    close(ev);
    if (psi >= 0) close(psi);
    close(cg);
    if (rmdir(path) < 0) perror("rmdir");
    return 0;
}
