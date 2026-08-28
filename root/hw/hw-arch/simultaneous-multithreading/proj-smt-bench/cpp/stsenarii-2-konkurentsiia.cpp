#include <iostream>
#include <thread>
#include <chrono>
#include <immintrin.h>
#include <pthread.h>
#include <sched.h>

constexpr uint64_t VEC_ITERS = 100000000ULL;

void vector_fma_worker(int cpu_id, double &elapsed_ms) {
    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    CPU_SET(cpu_id, &cpuset);
    pthread_setaffinity_np(pthread_self(), sizeof(cpu_set_t), &cpuset);

    const auto start = std::chrono::high_resolution_clock::now();

    __m256 a = _mm256_set1_ps(1.0001f);
    __m256 b = _mm256_set1_ps(1.0002f);
    __m256 c = _mm256_set1_ps(0.5f);

    for (uint64_t i = 0; i < VEC_ITERS; ++i) {
        a = _mm256_fmadd_ps(a, b, c);
        b = _mm256_fmadd_ps(b, a, c);
        a = _mm256_fmadd_ps(a, b, c);
        b = _mm256_fmadd_ps(b, a, c);
    }

    volatile float sink;
    float res[8];
    _mm256_storeu_ps(res, a);
    sink = res[0];
    (void)sink;

    const auto end = std::chrono::high_resolution_clock::now();
    elapsed_ms = std::chrono::duration<double, std::milli>(end - start).count();
}
