#include <immintrin.h>
#include <stdint.h>
#include <stddef.h>

// Паралельне ділення 8 елементів uint32_t на константу 10 за допомогою AVX2
void vec_div10_avx2(const uint32_t* src, uint32_t* dst, size_t count) {
    size_t i = 0;
    __m256i multiplier = _mm256_set1_epi64x(0xCCCCCCCDULL);
    
    for (; i + 7 < count; i += 8) {
        __m256i v = _mm256_loadu_si256((const __m256i*)(src + i));
        
        // Обробка парних 32-бітних елементів (0, 2, 4, 6)
        __m256i prod_even = _mm256_mul_epu32(v, multiplier);
        __m256i q_even = _mm256_srli_epi64(prod_even, 35);
        
        // Обробка непарних 32-бітних елементів (1, 3, 5, 7)
        __m256i v_odd = _mm256_srli_epi64(v, 32);
        __m256i prod_odd = _mm256_mul_epu32(v_odd, multiplier);
        __m256i q_odd = _mm256_srli_epi64(prod_odd, 35);
        
        // Об'єднуємо результати частки назад у 32-бітний вектор
        __m256i q_odd_shifted = _mm256_slli_epi64(q_odd, 32);
        __m256i res = _mm256_or_si256(q_even, q_odd_shifted);
        
        _mm256_storeu_si256((__m256i*)(dst + i), res);
    }
    
    // Скалярний хвіст масиву
    for (; i < count; i++) {
        dst[i] = src[i] / 10U;
    }
}
