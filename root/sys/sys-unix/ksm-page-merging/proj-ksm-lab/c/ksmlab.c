/* ksmlab.c — чи справді ядро злило ваші сторінки і в яких числах це видно.
   Складання: cc -O2 -Wall -Wextra -o ksmlab ksmlab.c
   Запуск:    sudo ./ksmlab      (root: KSM вмикається на рівні всієї системи)
   Потрібно:  CONFIG_KSM; поле ksm_process_profit у ksm_stat — з ядра 6.4,
              рядок KSM у smaps — з 6.6. */

#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <errno.h>
#include <fcntl.h>
#include <time.h>
#include <sched.h>
#include <signal.h>
#include <unistd.h>
#include <sys/mman.h>

#define KSM       "/sys/kernel/mm/ksm/"
#define PAGE      4096UL
#define NPAGES    16384UL            /* 64 МіБ на ділянку */
#define BYTES     (NPAGES * PAGE)
#define NPROBE    4096UL             /* скільки сторінок протикаємо на вимірі */
#define STRIDE    4099UL             /* просте, взаємно просте з 16384 —
                                        NPROBE різних сторінок без повторів */
#define SCAN_FAST 4000               /* pages_to_scan на час досліду */

/* На випадок старих заголовків: значення з asm-generic (x86-64, arm64…). */
#ifndef MADV_MERGEABLE
#define MADV_MERGEABLE   12
#endif
#ifndef MADV_NOHUGEPAGE
#define MADV_NOHUGEPAGE  15
#endif

static long ksm_get(const char *name)
{
    char path[128], buf[64];
    int fd;
    ssize_t n;

    snprintf(path, sizeof path, KSM "%s", name);
    if ((fd = open(path, O_RDONLY)) < 0) return -1;
    n = read(fd, buf, sizeof buf - 1);
    close(fd);
    if (n <= 0) return -1;
    buf[n] = '\0';
    return strtol(buf, NULL, 10);
}

static int put_raw(const char *path, const char *s, size_t len)
{
    int fd = open(path, O_WRONLY);
    ssize_t n;

    if (fd < 0) return -1;
    n = write(fd, s, len);
    close(fd);
    return n == (ssize_t)len ? 0 : -1;
}

static char run_back[24], scan_back[24];
static size_t run_len, scan_len;
static volatile sig_atomic_t knobs_taken;

static void restore_knobs(void)
{
    if (!knobs_taken) return;
    knobs_taken = 0;
    put_raw(KSM "pages_to_scan", scan_back, scan_len);
    put_raw(KSM "run", run_back, run_len);
}

static void on_signal(int sig)
{
    restore_knobs();          /* тільки open/write/close — безпечно в обробнику */
    _exit(128 + sig);
}

static void take_knobs(void)
{
    long run = ksm_get("run"), scan = ksm_get("pages_to_scan");
    char fast[24];
    int len;

    run_len  = (size_t)snprintf(run_back,  sizeof run_back,  "%ld\n", run);
    scan_len = (size_t)snprintf(scan_back, sizeof scan_back, "%ld\n", scan);
    len      = snprintf(fast, sizeof fast, "%d\n", SCAN_FAST);

    if (put_raw(KSM "run", "1\n", 2) != 0 ||
        put_raw(KSM "pages_to_scan", fast, (size_t)len) != 0) {
        fprintf(stderr, "не вдалося записати в " KSM ": %s\n"
                        "ці ручки належать root — спробуйте sudo\n", strerror(errno));
        exit(1);
    }
    knobs_taken = 1;
    atexit(restore_knobs);
    signal(SIGINT,  on_signal);
    signal(SIGTERM, on_signal);

    printf("run             : %ld → 1       (повернемо %ld)\n", run, run);
    printf("pages_to_scan   : %ld → %d    (повернемо %ld)\n", scan, SCAN_FAST, scan);
    printf("sleep_millisecs : %ld\n", ksm_get("sleep_millisecs"));
}
