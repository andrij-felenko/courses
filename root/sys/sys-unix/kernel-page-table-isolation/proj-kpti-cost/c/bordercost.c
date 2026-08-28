/* bordercost.c — ціна перетину межі ядра на цій машині.
 *
 *   cc -O2 -Wall -Wextra -o bordercost bordercost.c
 *   taskset -c 3 ./bordercost 3
 *
 * Лише x86-64 (RDTSC/RDTSCP). Прав root не потребує. */

#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <errno.h>
#include <time.h>
#include <unistd.h>
#include <sched.h>
#include <sys/mman.h>
#include <sys/syscall.h>
#include <x86intrin.h>

#define PAGE       4096u
#define STEPS        64      /* сторінок, яких торкаємося між двома викликами */
#define MAX_KIB  262144u     /* 256 МіБ — стеля розгортки */

/* RDTSC бар'єром не є: процесор має право виконати її раніше або пізніше
   за сусідні інструкції. Тому початок вікна затискаємо між двома LFENCE,
   а кінець беремо RDTSCP (вона сама чекає завершення попереднього)
   і закриваємо ще одним LFENCE, щоб наступне не заповзло всередину. */
static inline uint64_t tsc_open(void)
{
    _mm_lfence();
    uint64_t t = __rdtsc();
    _mm_lfence();
    return t;
}

static inline uint64_t tsc_close(void)
{
    unsigned aux;
    uint64_t t = __rdtscp(&aux);
    _mm_lfence();
    return t;
}

/* Скільки тактів TSC припадає на секунду. Питати про це рядок model name
   у /proc/cpuinfo не можна: TSC цокає зі сталою частотою незалежно від
   того, на якій частоті зараз працює ядро процесора. Єдиний надійний
   спосіб — звірити лічильник із годинником ядра. */
static double tsc_hz(void)
{
    struct timespec a, b, nap = { 0, 200 * 1000 * 1000 };   /* 200 мс */
    uint64_t c0, c1;
    double ns;

    clock_gettime(CLOCK_MONOTONIC, &a);
    c0 = tsc_open();
    while (nanosleep(&nap, &nap) == -1 && errno == EINTR)
        ;
    c1 = tsc_close();
    clock_gettime(CLOCK_MONOTONIC, &b);

    ns = (double)(b.tv_sec - a.tv_sec) * 1e9
       + (double)(b.tv_nsec - a.tv_nsec);
    return (double)(c1 - c0) * 1e9 / ns;
}
