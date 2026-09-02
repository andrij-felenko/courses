#define _GNU_SOURCE
#include "chunks.h"
#include "proc_sum.h"
#include "thread_sum.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define N        (8u * 1024u * 1024u)   /* 8 Мі елементів ≈ 32 МіБ */
#define WORKERS  4

static double now_ms(void)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec * 1000.0 + ts.tv_nsec / 1e6;
}

int main(void)
{
    int *data = malloc((size_t)N * sizeof *data);
    if (data == NULL) {
        fprintf(stderr, "не вистачило пам'яті під масив\n");
        return EXIT_FAILURE;
    }
    for (size_t i = 0; i < N; ++i)
        data[i] = (int)(i % 7) - 3;

    const chunk_t whole = { .start = 0, .end = N };
    const long long reference = sum_range(data, whole);

    puts("--- ПОТОКИ: спільний адресний простір, обмін через покажчик ---");
    long long thread_total = 0;
    double t0 = now_ms();
    int rc = thread_sum(data, N, WORKERS, &thread_total);
    double t1 = now_ms();
    if (rc != 0) {
        fprintf(stderr, "thread_sum: %s\n", strerror(rc));
        free(data);
        return EXIT_FAILURE;
    }
    printf("  сума = %lld, час = %.2f мс\n\n", thread_total, t1 - t0);

    puts("--- ПРОЦЕСИ: копія-при-записі, обмін через канал ---");
    /* Форкаємо, коли робочі потоки вже приєднані й у процесі знову лишився
       один головний потік. fork() копіює ЛИШЕ того, хто його викликав, тож
       м'ютекс, захоплений чужим потоком, застряг би в дитині назавжди. */
    long long proc_total = 0;
    t0 = now_ms();
    rc = proc_sum(data, N, WORKERS, &proc_total);
    t1 = now_ms();
    if (rc != 0) {
        fprintf(stderr, "proc_sum: %s\n", strerror(rc));
        free(data);
        return EXIT_FAILURE;
    }
    printf("  сума = %lld, час = %.2f мс\n\n", proc_total, t1 - t0);

    printf("контроль = %lld; обидві відповіді збіглися: %s\n", reference,
           (thread_total == reference && proc_total == reference) ? "так" : "НІ");

    free(data);
    return EXIT_SUCCESS;
}
