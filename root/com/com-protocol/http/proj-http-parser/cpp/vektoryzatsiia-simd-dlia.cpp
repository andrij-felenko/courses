#include <immintrin.h>

// Пошук символу '\n' у 32-байтному блоці за допомогою AVX2
size_t find_newline_avx2(const char* buf, size_t len) {
    size_t i = 0;
    __m256i target = _mm256_set1_epi8('\n');
    
    for (; i + 32 <= len; i += 32) {
        __m256i chunk = _mm256_loadu_si256(reinterpret_cast<const __m256i*>(buf + i));
        __m256i cmp = _mm256_cmpeq_epi8(chunk, target);
        unsigned int mask = _mm256_movemask_epi8(cmp);
        if (mask != 0) {
            // __builtin_ctz знаходить індекс першого встановленого біта
            return i + __builtin_ctz(mask);
        }
    }
    // Дообробка залишку менше 32 байтів класичним циклом
    for (; i < len; ++i) {
        if (buf[i] == '\n') return i;
    }
    return std::string_view::npos;
}
