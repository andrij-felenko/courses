/* adev.c — перекривна девіація Аллана з журналу відносної частоти.
   Збірка:  cc -O2 -o adev adev.c -lm
   Виклик:  ./adev 1.0 < y.txt      // 1.0 — крок вимірювання τ₀, секунди
   Рядок журналу: число y (відносне відхилення частоти) або «*» — пропуск. */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define MIN_SPANS 10   /* менш як стільки незалежних відрізків τ у записі — не рахуємо */

int main(int argc, char **argv)
{
    double tau0 = (argc > 1) ? atof(argv[1]) : 1.0;

    /* 1. Прочитати журнал. Усе, що не парситься у скінченне число, — пропуск. */
    size_t cap = 4096, M = 0;
    double *y    = malloc(cap * sizeof *y);
    char   *miss = malloc(cap);
    if (!y || !miss) { perror("malloc"); return 1; }

    char buf[128];
    while (fgets(buf, sizeof buf, stdin)) {
        if (M == cap) {
            cap *= 2;
            y    = realloc(y, cap * sizeof *y);
            miss = realloc(miss, cap);
            if (!y || !miss) { perror("realloc"); return 1; }
        }
        char *end;
        double v = strtod(buf, &end);
        int ok = (end != buf) && isfinite(v);
        y[M]    = ok ? v : 0.0;
        miss[M] = !ok;
        M++;
    }
    if (M < 4) { fprintf(stderr, "замало даних\n"); return 1; }

    /* 2. Зняти середню частоту: девіація Аллана від сталого зсуву не залежить,
          а великий зсув під час інтегрування з'їдає значущі цифри. */
    double sum = 0.0;
    size_t nv = 0;
    for (size_t i = 0; i < M; i++)
        if (!miss[i]) { sum += y[i]; nv++; }
    double mean = nv ? sum / nv : 0.0;

    /* 3. Один прохід: фаза x (секунди) і наростальний лічильник пропусків.
          Фазових точок на одну більше, ніж вимірів. */
    size_t N = M + 1;
    double   *x  = malloc(N * sizeof *x);
    unsigned *ng = malloc(N * sizeof *ng);
    if (!x || !ng) { perror("malloc"); return 1; }
    x[0] = 0.0;
    ng[0] = 0;
    for (size_t i = 0; i < M; i++) {
        x[i + 1]  = x[i] + (miss[i] ? 0.0 : y[i] - mean) * tau0;
        ng[i + 1] = ng[i] + (unsigned) miss[i];
    }

    /* 4. Драбина τ октавами: m = 1, 2, 4, 8, … */
    printf("#   tau, s      sigma_y(tau)   доданків   відрізків\n");
    for (size_t m = 1; 2 * m < N && N / m >= MIN_SPANS; m *= 2) {
        double acc = 0.0;
        size_t k = 0;
        for (size_t i = 0; i + 2 * m < N; i++) {
            if (ng[i + 2 * m] != ng[i]) continue;   /* трійка накрила пропуск */
            double d = x[i + 2 * m] - 2.0 * x[i + m] + x[i];
            acc += d * d;
            k++;
        }
        if (k < 2) continue;
        double tau  = (double) m * tau0;
        double avar = acc / (2.0 * tau * tau * (double) k);
        printf("%9.4g  %14.4e  %9zu  %9zu\n", tau, sqrt(avar), k, N / m);
    }

    free(y); free(miss); free(x); free(ng);
    return 0;
}
