#define _GNU_SOURCE
#include <stdint.h>
#include <time.h>

static int64_t now_ns(clockid_t clk)
{
    struct timespec ts;
    clock_gettime(clk, &ts);
    return (int64_t)ts.tv_sec * 1000000000LL + ts.tv_nsec;
}

/* Скільки машина проспала від увімкнення. Величина монотонно зростає. */
static int64_t slept_ns(void)
{
    return now_ns(CLOCK_BOOTTIME) - now_ns(CLOCK_MONOTONIC);
}
