/* setbright.c — виставити яскравість панелі.
 *   cc -O2 -Wall -Wextra -o setbright setbright.c
 *   chown root:video setbright && chmod 4750 setbright
 */
#define _GNU_SOURCE
#include <dirent.h>
#include <errno.h>
#include <fcntl.h>
#include <grp.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/resource.h>
#include <sys/syscall.h>
#include <unistd.h>

#define PANEL "/sys/class/backlight/intel_backlight/brightness"
#define LIMIT "/sys/class/backlight/intel_backlight/max_brightness"

static void die(const char *msg)
{
    write(2, msg, strlen(msg));
    write(2, "\n", 1);
    _exit(1);
}

/* 1. Дескриптори 0, 1, 2 мусять існувати ДО першого open() у програмі */
static void ensure_std_fds(void)
{
    for (int fd = 0; fd <= 2; fd++) {
        if (fcntl(fd, F_GETFD) != -1)
            continue;
        if (errno != EBADF || open("/dev/null", O_RDWR) != fd)
            _exit(1);
    }
}

/* 2. Усе, що вище 2, — чуже */
static void close_inherited(void)
{
#ifdef SYS_close_range
    if (syscall(SYS_close_range, 3u, ~0u, 0) == 0)   /* Linux 5.9+ */
        return;
#endif
    DIR *d = opendir("/proc/self/fd");
    if (!d)
        _exit(1);                     /* не знаємо спадку — не працюємо */

    int keep = dirfd(d);
    struct dirent *e;
    while ((e = readdir(d)) != NULL) {
        int fd = atoi(e->d_name);     /* "." і ".." дають 0 */
        if (fd > 2 && fd != keep)
            close(fd);
    }
    closedir(d);
}

/* 3. Решта успадкованого стану */
static void reset_inherited_state(void)
{
    clearenv();                       /* своє оточення, а не чуже почищене */

    sigset_t none;
    sigemptyset(&none);
    sigprocmask(SIG_SETMASK, &none, NULL);    /* маска переживає exec */

    struct rlimit unbound = { RLIM_INFINITY, RLIM_INFINITY };
    if (setrlimit(RLIMIT_FSIZE, &unbound) != 0)
        die("не зняти обмеження на розмір запису");

    if (chdir("/") != 0)
        die("немає доступу до /");
    umask(022);
}

/* 4. Зниження прав остаточне — і перевірене */
static void drop_privileges_forever(void)
{
    uid_t ru = getuid();
    gid_t rg = getgid();

    if (setgroups(0, NULL) != 0 ||
        setresgid(rg, rg, rg) != 0 ||
        setresuid(ru, ru, ru) != 0)
        die("зниження прав не вдалося");

    uid_t r, e, s;
    gid_t gr, ge, gs;
    if (getresuid(&r, &e, &s) != 0 || r != ru || e != ru || s != ru)
        die("права лишилися підвищеними");
    if (getresgid(&gr, &ge, &gs) != 0 || gr != rg || ge != rg || gs != rg)
        die("групові права лишилися підвищеними");
}

static long panel_max(void)
{
    char buf[32];
    int fd = open(LIMIT, O_RDONLY | O_CLOEXEC);
    if (fd < 0)
        die("немає max_brightness");
    ssize_t n = read(fd, buf, sizeof buf - 1);
    close(fd);
    if (n <= 0)
        die("порожній max_brightness");
    buf[n] = '\0';
    return strtol(buf, NULL, 10);
}

int main(int argc, char **argv)
{
    ensure_std_fds();
    close_inherited();
    reset_inherited_state();

    if (argc != 2)                    /* argc == 0 сюди теж не пройде */
        die("вжиток: setbright <рівень>");

    /* єдина дія, заради якої потрібен root */
    int panel = open(PANEL, O_WRONLY | O_CLOEXEC);
    if (panel < 0)
        die("панель недоступна");

    drop_privileges_forever();

    /* далі — жодних прав понад ті, що має той, хто викликав */
    char *end;
    errno = 0;
    long want = strtol(argv[1], &end, 10);
    if (errno != 0 || end == argv[1] || *end != '\0')
        die("рівень має бути числом");

    long max = panel_max();
    if (want < 1 || want > max)
        die("рівень поза межами панелі");

    char out[32];
    int len = snprintf(out, sizeof out, "%ld", want);
    if (write(panel, out, len) != len)
        die("запис не пройшов");
    return 0;
}
