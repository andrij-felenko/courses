#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <pthread.h>
#include <sched.h>
#include <immintrin.h>
#include <time.h>

#define VEC_ITERS 100000000ULL

typedef struct {
    int cpu_id;
    double elapsed_ms;
} vec_arg_t;

void* vector_fma_worker(void *arg) {
    vec_arg_t *tdata = (vec_arg_t*)arg;

    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    CPU_SET(tdata->cpu_id, &cpuset);
    pthread_setaffinity_np(pthread_self(), sizeof(cpu_set_t), &cpuset);

    struct timespec ts0, ts1;
    clock_gettime(CLOCK_MONOTONIC, &ts0);

    // Завантажуємо вектори в регістри YMM
    __m256 a = _mm256_set1_ps(1.0001f);
    __m256 b = _mm256_set1_ps(1.0002f);
    __m256 c = _mm256_set1_ps(0.5f);

    for (uint64_t i = 0; i < VEC_ITERS; ++i) {
        // Чотири незалежні операції FMA для розгортання та утилізації портів
        a = _mm256_fmadd_ps(a, b, c);
        b = _mm256_fmadd_ps(b, a, c);
        a = _mm256_fmadd_ps(a, b, c);
        b = _mm256_fmadd_ps(b, a, c);
    }

    // Запобігаємо оптимізації компілятора
    volatile float sink;
    float res[8];
    _mm256_storeu_ps(res, a);
    sink = res[0];
    (void)sink;

    clock_gettime(CLOCK_MONOTONIC, &ts1);
    tdata->elapsed_ms = (double)(ts1.tv_sec - ts0.tv_sec) * 1000.0 +
                        (double)(ts1.tv_nsec - ts0.tv_nsec) / 1000000.0;
    return NULL;
}
