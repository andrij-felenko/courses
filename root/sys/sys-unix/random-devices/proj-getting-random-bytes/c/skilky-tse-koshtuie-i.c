#include <sys/syscall.h>
#include <sys/random.h>
#include <unistd.h>
#include <time.h>
#include <stdio.h>
#include <stdint.h>

static double now_ns(void)
{
    struct timespec t;
    clock_gettime(CLOCK_MONOTONIC, &t);
    return t.tv_sec * 1e9 + t.tv_nsec;
}

static ssize_t raw_getrandom(void *b, size_t n, unsigned f)
{
    return syscall(SYS_getrandom, b, n, f);   /* завжди справжній виклик */
}

int main(void)
{
    enum { N = 1000000 };
    uint8_t key[32];

    double t0 = now_ns();
    for (long i = 0; i < N; i++) getrandom(key, sizeof key, 0);
    double t1 = now_ns();
    for (long i = 0; i < N; i++) raw_getrandom(key, sizeof key, 0);
    double t2 = now_ns();

    printf("libc: %.1f нс   виклик: %.1f нс\n",
           (t1 - t0) / N, (t2 - t1) / N);
    return 0;
}
