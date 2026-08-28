/* thpprobe.c — скільки блоків порядку 9 система дасть НАСПРАВДІ.
   Збірка: cc -O2 -std=gnu11 -o thpprobe thpprobe.c
   Запуск: ./thpprobe [--count 128] [--collapse]

   без ключів   MADV_HUGEPAGE + дотик: тиха спроба, відмову рахуємо самі
   --collapse   MADV_COLLAPSE на кожен шматок: синхронно, з errno            */
#define _GNU_SOURCE
#include <errno.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>
#include <sys/mman.h>

#ifndef MADV_COLLAPSE
#define MADV_COLLAPSE 25          /* Linux 6.1; старі заголовки його не знають */
#endif

#define THP "/sys/kernel/mm/transparent_hugepage/"

static long sysfs_num(const char *path)
{
    FILE *f = fopen(path, "re");
    if (!f) return -1;
    long v;
    if (fscanf(f, "%ld", &v) != 1) v = -1;
    fclose(f);
    return v;
}

/* Лічильник із /proc/vmstat: рядки вигляду «ключ ЧИСЛО».
   Пробіл після ключа обов'язковий — інакше «thp_fault_fallback» злапає
   сусідній рядок «thp_fault_fallback_charge» і поверне зовсім інше число. */
static long vmstat(const char *key)
{
    FILE *f = fopen("/proc/vmstat", "re");
    if (!f) return -1;
    const size_t klen = strlen(key);
    char line[128];
    long v = -1;
    while (fgets(line, sizeof line, f))
        if (!strncmp(line, key, klen) && line[klen] == ' ') {
            v = strtol(line + klen + 1, NULL, 10);
            break;
        }
    fclose(f);
    return v;
}

/* AnonHugePages з /proc/self/smaps_rollup, у кілобайтах.
   У /proc/self/status цього поля немає — там лише RssAnon і RssFile. */
static long anon_thp_kb(void)
{
    FILE *f = fopen("/proc/self/smaps_rollup", "re");
    if (!f) return -1;
    char line[160];
    long v = -1;
    while (fgets(line, sizeof line, f))
        if (!strncmp(line, "AnonHugePages:", 14)) {
            v = strtol(line + 14, NULL, 10);
            break;
        }
    fclose(f);
    return v;
}

static double now_us(void)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec * 1e6 + ts.tv_nsec / 1e3;
}

static int cmp_d(const void *a, const void *b)
{
    double x = *(const double *) a, y = *(const double *) b;
    return (x > y) - (x < y);
}
