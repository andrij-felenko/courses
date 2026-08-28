/* bench_wc.c — Вимірювання пропускної здатності запису в пам'ять */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <time.h>
#include <immintrin.h>

#define BUFFER_SIZE_BYTES (64 * 1024 * 1024) /* 64 МіБ — більше за будь-який L3 кеш */
#define ITERATIONS 20

static inline double get_time_sec(void)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (double)ts.tv_sec + (double)ts.tv_nsec * 1e-9;
}

/* 1. Скалярний запис (Write-Back зі звичайним трафіком RFO) */
static void write_scalar(uint64_t *buf, size_t count, uint64_t val)
{
    for (size_t i = 0; i < count; ++i) {
        buf[i] = val;
    }
}

/* 2. Векторний кешований запис (AVX2 Write-Back) */
static void write_avx2_cached(void *buf, size_t bytes, __m256i val)
{
    __m256i *ptr = (__m256i *)buf;
    size_t count = bytes / sizeof(__m256i);
    for (size_t i = 0; i < count; ++i) {
        _mm256_storeu_si256(&ptr[i], val);
    }
}

/* 3. Потоковий нетемпоральний запис (Write-Combining через LFB) */
static void write_avx2_stream(void *buf, size_t bytes, __m256i val)
{
    __m256i *ptr = (__m256i *)buf;
    size_t count = bytes / sizeof(__m256i);
    for (size_t i = 0; i < count; ++i) {
        _mm256_stream_si256(&ptr[i], val);
    }
    /* Бар'єр упорядкування для скидання залишків буферів злиття */
    _mm_sfence();
}

int main(void)
{
    void *raw_buf = NULL;
    /* Виділяємо пам'ять із вирівнюванням на 64 байти (розмір рядка кешу) */
    if (posix_memalign(&raw_buf, 64, BUFFER_SIZE_BYTES) != 0) {
        perror("posix_memalign failed");
        return 1;
    }

    uint64_t *buf64 = (uint64_t *)raw_buf;
    size_t u64_count = BUFFER_SIZE_BYTES / sizeof(uint64_t);
    __m256i pattern = _mm256_set1_epi64x(0xAAAAAAAAAAAAAAAAULL);

    printf("=== Бенчмарк пропускної здатності запису (Буфер: %d МіБ) ===\n",
           BUFFER_SIZE_BYTES / (1024 * 1024));

    /* Тест 1: Скалярний запис */
    {
        double t0 = get_time_sec();
        for (int it = 0; it < ITERATIONS; ++it) {
            write_scalar(buf64, u64_count, 0xAAAAAAAAAAAAAAAAULL + it);
        }
        double dt = get_time_sec() - t0;
        double gb = (double)BUFFER_SIZE_BYTES * ITERATIONS / (1024.0 * 1024.0 * 1024.0);
        printf("[1] Скалярний Write-Back (RFO):       %6.2f ГБ/с (час: %.3f с)\n", gb / dt, dt);
    }

    /* Тест 2: Векторний кешований запис */
    {
        double t0 = get_time_sec();
        for (int it = 0; it < ITERATIONS; ++it) {
            write_avx2_cached(raw_buf, BUFFER_SIZE_BYTES, pattern);
        }
        double dt = get_time_sec() - t0;
        double gb = (double)BUFFER_SIZE_BYTES * ITERATIONS / (1024.0 * 1024.0 * 1024.0);
        printf("[2] Векторний AVX2 Write-Back:         %6.2f ГБ/с (час: %.3f с)\n", gb / dt, dt);
    }

    /* Тест 3: Нетемпоральний потоковий запис */
    {
        double t0 = get_time_sec();
        for (int it = 0; it < ITERATIONS; ++it) {
            write_avx2_stream(raw_buf, BUFFER_SIZE_BYTES, pattern);
        }
        double dt = get_time_sec() - t0;
        double gb = (double)BUFFER_SIZE_BYTES * ITERATIONS / (1024.0 * 1024.0 * 1024.0);
        printf("[3] Потоковий Write-Combining (NT):   %6.2f ГБ/с (час: %.3f с)\n", gb / dt, dt);
    }

    free(raw_buf);
    return 0;
}
