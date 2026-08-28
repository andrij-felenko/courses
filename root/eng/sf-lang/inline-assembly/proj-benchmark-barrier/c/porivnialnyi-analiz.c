#include <stdint.h>
#include <immintrin.h>

/* Варіант 1: Вбудований асемблер (не підтримує згортання констант) */
int count_leading_zeros_asm(uint32_t val) {
    if (val == 0) return 32;
    int res;
    __asm__ ("bsrl %1, %0" : "=r" (res) : "r" (val) : "cc");
    return 31 - res;
}

/* Варіант 2: Вбудована функція компілятора (повна оптимізація в IR) */
int count_leading_zeros_intrinsic(uint32_t val) {
    if (val == 0) return 32;
    return __builtin_clz(val); /* Автоматично генерує LZCNT або BSR */
}

/* Паралельне векторне додавання через SSE Intrinsics */
void add_vectors_sse(const float *a, const float *b, float *result) {
    __m128 va = _mm_loadu_ps(a);
    __m128 vb = _mm_loadu_ps(b);
    __m128 vres = _mm_add_ps(va, vb);
    _mm_storeu_ps(result, vres);
}
