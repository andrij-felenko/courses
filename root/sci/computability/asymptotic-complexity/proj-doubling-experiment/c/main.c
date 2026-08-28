#include <stdio.h>
#include <stdlib.h>
#include <time.h>

static double now(void)                 /* монотонний годинник у секундах (POSIX; */
{                                        /* на Windows — QueryPerformanceCounter)  */
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec + ts.tv_nsec * 1e-9;
}

static volatile long sink;              /* сток проти видалення циклу оптимізатором */

/* Найкоротший (найменш зашумлений) час проходу масивом — O(n). */
static double time_pass(const int *a, size_t n, int reps)
{
    double best = 1e300;
    for (int r = 0; r < reps; r++) {
        double t0 = now();
        long s = 0;
        for (size_t i = 0; i < n; i++)
            s += a[i];
        double dt = now() - t0;
        sink = s;                       /* «використали» суму — інакше цикл викинуть */
        if (dt < best) best = dt;       /* мінімум: шум лише додає час, не віднімає */
    }
    return best;
}

int main(void)
{
    double prev = 0.0;
    for (size_t n = 1u << 12; n <= 1u << 22; n <<= 1) {   /* 4К … 4М, подвоєння */
        int *a = malloc(n * sizeof *a);
        for (size_t i = 0; i < n; i++) a[i] = (int)(i & 0x3f);
        double t = time_pass(a, n, 21);
        if (prev > 0.0)
            printf("n=%9zu  t=%.3e с  T(2n)/T(n)=%.2f\n", n, t, t / prev);
        else
            printf("n=%9zu  t=%.3e с  T(2n)/T(n)=  —\n", n, t);
        prev = t;
        free(a);
    }
    return 0;
}
