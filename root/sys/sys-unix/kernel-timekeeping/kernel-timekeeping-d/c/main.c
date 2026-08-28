#include <time.h>
#include <stdint.h>
#include <stdio.h>

void do_work(void);

/* Тривалість у наносекундах між двома знятими моментами. */
static int64_t elapsed_ns(const struct timespec *a, const struct timespec *b)
{
    return (int64_t)(b->tv_sec - a->tv_sec) * 1000000000LL
         + (int64_t)(b->tv_nsec - a->tv_nsec);
}

void measure(void)
{
    struct timespec t0, t1;

    clock_gettime(CLOCK_MONOTONIC, &t0);   /* не REALTIME */
    do_work();
    clock_gettime(CLOCK_MONOTONIC, &t1);

    printf("%lld нс\n", (long long)elapsed_ns(&t0, &t1));
}
