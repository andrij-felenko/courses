/* clocklab.c — що машина знає про час і скільки це знання коштує.
   Складання: cc -O2 -Wall -Wextra -o clocklab clocklab.c
   Запуск:    ./clocklab      (звичайний користувач; root не потрібен) */

#define _GNU_SOURCE
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <errno.h>
#include <time.h>
#include <sched.h>
#include <unistd.h>
#include <sys/syscall.h>
#include <sys/timex.h>

static int64_t to_ns(const struct timespec *t)
{
    return (int64_t)t->tv_sec * 1000000000LL + t->tv_nsec;
}

static const struct { clockid_t id; const char *name; } CLOCKS[] = {
    { CLOCK_REALTIME,         "CLOCK_REALTIME"         },
    { CLOCK_REALTIME_COARSE,  "CLOCK_REALTIME_COARSE"  },
    { CLOCK_MONOTONIC,        "CLOCK_MONOTONIC"        },
    { CLOCK_MONOTONIC_COARSE, "CLOCK_MONOTONIC_COARSE" },
    { CLOCK_MONOTONIC_RAW,    "CLOCK_MONOTONIC_RAW"    },
    { CLOCK_BOOTTIME,         "CLOCK_BOOTTIME"         },
    { CLOCK_TAI,              "CLOCK_TAI"              },
};
#define NCLOCKS (sizeof CLOCKS / sizeof CLOCKS[0])

static void show_clocks(void)
{
    /* Заголовок — готовим рядком: %-24s рівняє за БАЙТАМИ, а українська
       літера в UTF-8 займає два, тож колонки поїхали б. */
    puts("годинник                          значення, с   роздільність");

    for (size_t i = 0; i < NCLOCKS; i++) {
        struct timespec t, r;

        if (clock_gettime(CLOCKS[i].id, &t) != 0) {
            printf("%-24s   недоступний: %s\n", CLOCKS[i].name, strerror(errno));
            continue;
        }
        clock_getres(CLOCKS[i].id, &r);

        printf("%-24s %13lld.%06ld %14lld\n", CLOCKS[i].name,
               (long long)t.tv_sec, (long)(t.tv_nsec / 1000),
               (long long)to_ns(&r));
    }
}

static void show_gaps(void)
{
    struct timespec mono, boot, raw, real;

    clock_gettime(CLOCK_MONOTONIC,     &mono);
    clock_gettime(CLOCK_BOOTTIME,      &boot);
    clock_gettime(CLOCK_MONOTONIC_RAW, &raw);
    clock_gettime(CLOCK_REALTIME,      &real);

    printf("BOOTTIME − MONOTONIC      = %12.3f с  — стільки система спала\n",
           (to_ns(&boot) - to_ns(&mono)) / 1e9);
    printf("MONOTONIC_RAW − MONOTONIC = %12.6f с  — стільки набігло поправки\n",
           (to_ns(&raw) - to_ns(&mono)) / 1e9);
    printf("REALTIME − MONOTONIC      = %12.3f с  — зміщення до епохи\n",
           (to_ns(&real) - to_ns(&mono)) / 1e9);
}
