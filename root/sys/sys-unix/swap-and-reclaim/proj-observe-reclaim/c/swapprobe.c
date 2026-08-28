/* swapprobe.c — витіснити власну ділянку й виміряти ціну її повернення
 * збірка: cc -O2 -Wall -Wextra -o swapprobe swapprobe.c
 * запуск: ./swapprobe [МіБ] [r|w]   — типово 256 МіБ, повернення читанням */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <unistd.h>
#include <time.h>
#include <sys/mman.h>
#include <sys/resource.h>

#ifndef MADV_COLD
#define MADV_COLD     20
#endif
#ifndef MADV_PAGEOUT
#define MADV_PAGEOUT  21
#endif

static long PAGE;

static long long now_ns(void)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (long long)ts.tv_sec * 1000000000LL + ts.tv_nsec;
}

/* скільки сторінок ділянки просто зараз відображені в наші таблиці сторінок */
static size_t resident_pages(void *a, size_t len)
{
    size_t n = len / (size_t)PAGE, i, live = 0;
    unsigned char *vec = malloc(n);
    if (!vec) { perror("malloc"); exit(1); }
    if (mincore(a, len, vec) != 0) { perror("mincore"); exit(1); }
    for (i = 0; i < n; i++)
        if (vec[i] & 1u) live++;
    free(vec);
    return live;
}

/* одне поле з /proc/self/status, у кілобайтах; −1, якщо поля немає */
static long status_kb(const char *key)
{
    char line[256];
    long val = -1;
    size_t klen = strlen(key);
    FILE *f = fopen("/proc/self/status", "r");
    if (!f) { perror("/proc/self/status"); exit(1); }
    while (fgets(line, sizeof line, f))
        if (strncmp(line, key, klen) == 0 && line[klen] == ':') {
            sscanf(line + klen + 1, "%ld", &val);
            break;
        }
    fclose(f);
    return val;
}

static long major_faults(void)
{
    struct rusage ru;
    getrusage(RUSAGE_SELF, &ru);
    return ru.ru_majflt;
}

/* по одному доступу на сторінку; volatile — щоб компілятор не викинув цикл */
static void touch(void *a, size_t len, int write)
{
    volatile unsigned char *p = a;
    unsigned sink = 0;
    size_t i;
    for (i = 0; i < len; i += (size_t)PAGE) {
        if (write) p[i] = 1;
        else       sink += p[i];
    }
    (void)sink;
}

static void snapshot(const char *label, void *a, size_t len)
{
    printf("%s\n"
           "   резидентних %6zu з %zu   RssAnon %8ld кБ"
           "   VmSwap %8ld кБ   majflt %ld\n",
           label, resident_pages(a, len), len / (size_t)PAGE,
           status_kb("RssAnon"), status_kb("VmSwap"), major_faults());
}

/* MADV_PAGEOUT лише запускає роботу: хвіст сторінок ще під записом у своп.
   Чекаємо, доки резидентність перестане падати, але не довше за ms. */
static size_t settle(void *a, size_t len, int ms)
{
    struct timespec nap = { 0, 20 * 1000 * 1000 };
    long long deadline = now_ns() + (long long)ms * 1000000LL;
    size_t prev = resident_pages(a, len), cur;
    for (;;) {
        nanosleep(&nap, NULL);
        cur = resident_pages(a, len);
        if (cur == 0 || cur == prev || now_ns() > deadline) return cur;
        prev = cur;
    }
}

static int have_swap(void)
{
    char line[256];
    int rows = 0;
    FILE *f = fopen("/proc/swaps", "r");
    if (!f) return 0;
    while (fgets(line, sizeof line, f)) rows++;
    fclose(f);
    return rows > 1;                      /* перший рядок — заголовок */
}

int main(int argc, char **argv)
{
    size_t mib   = (argc > 1) ? (size_t)strtoul(argv[1], NULL, 10) : 256;
    int    wmode = (argc > 2 && argv[2][0] == 'w');
    size_t len, pages, left;
    void  *a;
    long long t0, t1;
    long mf0, mf1;
    double us;

    PAGE = sysconf(_SC_PAGESIZE);
    if (mib == 0) { fprintf(stderr, "розмір має бути більший за нуль\n"); return 2; }
    len   = mib * 1024 * 1024;
    pages = len / (size_t)PAGE;

    if (!have_swap())
        fprintf(stderr, "УВАГА: жодної області свопу — анонімним сторінкам "
                        "нікуди йти, витіснення не станеться\n");

    a = mmap(NULL, len, PROT_READ | PROT_WRITE,
             MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if (a == MAP_FAILED) { perror("mmap"); return 1; }

    /* без цього одиницею роботи стануть 2 МіБ замість сторінки */
    if (madvise(a, len, MADV_NOHUGEPAGE) != 0)
        fprintf(stderr, "MADV_NOHUGEPAGE: %s — числа будуть грубіші\n",
                strerror(errno));

    snapshot("1 щойно виділено", a, len);

    touch(a, len, 1);
    snapshot("2 після торкання", a, len);

    if (madvise(a, len, MADV_PAGEOUT) != 0) {
        fprintf(stderr, "MADV_PAGEOUT: %s (потрібен Linux 5.4+)\n",
                strerror(errno));
        return 1;
    }
    left = settle(a, len, 5000);
    if (left)
        fprintf(stderr, "лишилося резидентними %zu сторінок: "
                        "MADV_PAGEOUT — підказка, а не наказ\n", left);
    snapshot("3 після MADV_PAGEOUT", a, len);

    mf0 = major_faults();
    t0  = now_ns();
    touch(a, len, wmode);
    t1  = now_ns();
    mf1 = major_faults();

    snapshot("4 після повернення", a, len);

    us = (double)(t1 - t0) / 1000.0;
    printf("\nповернення %zu сторінок (%zu МіБ) %s\n",
           pages, mib, wmode ? "записом" : "читанням");
    printf("  великих збоїв   %ld  (%.1f %% сторінок)\n",
           mf1 - mf0, 100.0 * (double)(mf1 - mf0) / (double)pages);
    printf("  час             %.1f мс\n", us / 1000.0);
    printf("  на сторінку     %.1f мкс\n", us / (double)pages);
    if (mf1 > mf0)
        printf("  на великий збій %.1f мкс\n", us / (double)(mf1 - mf0));

    munmap(a, len);
    return 0;
}
