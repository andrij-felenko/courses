/* bench.c — три способи спитати й що вони коштують.  gcc -O2 -o bench bench.c */
#include <stdio.h>
#include <time.h>

#define SYS_getpid 39                          /* x86-64; на aarch64 — 172 */

static inline long raw_getpid(void)
{
    long ret;
    __asm__ volatile ("syscall"
                      : "=a" (ret)
                      : "a" ((long) SYS_getpid)
                      : "rcx", "r11", "memory");
    return ret;
}

__attribute__((noinline)) static long plain(long x) { return x + 1; }

static double now_ns(void)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);       /* сам іде через vDSO, тому дешевий */
    return ts.tv_sec * 1e9 + ts.tv_nsec;
}

#define TIME(label, N, body) do {                                   \
        double t0 = now_ns();                                       \
        for (long i = 0; i < (N); i++) { body; }                    \
        printf("%s: %.1f нс на виклик\n", label, (now_ns() - t0) / (N)); \
    } while (0)

int main(void)
{
    volatile long sink = 0;
    struct timespec ts;

    TIME("виклик функції",       200000000L, sink = plain(i));
    TIME("clock_gettime (vDSO)",  20000000L, clock_gettime(CLOCK_MONOTONIC, &ts));
    TIME("getpid (голий syscall)", 5000000L, sink = raw_getpid());
    return 0;
}
