#include <immintrin.h>
#include <stddef.h>
#include <stdint.h>

/* Векторний підрахунок частоти кандидата через AVX2 */
size_t count_frequency_avx2(const int32_t *data, size_t size, int32_t target) {
    size_t count = 0;
    size_t i = 0;

    __m256i target_vec = _mm256_set1_epi32(target);

    /* Обробка блоками по 8 елементів (256 біт) */
    for (; i + 8 <= size; i += 8) {
        __m256i chunk = _mm256_loadu_si256((const __m256i*)(data + i));
        __m256i match = _mm256_cmpeq_epi32(chunk, target_vec);
        int mask = _mm256_movemask_epi8(match);
        if (mask != 0) {
            /* Кожен збіг 32-бітного числа дає 4 біти в масці movemask */
            count += (size_t)__builtin_popcount(mask) / 4;
        }
    }

    /* Дообробка залишку масиву */
    for (; i < size; ++i) {
        if (data[i] == target) {
            count++;
        }
    }

    return count;
}
