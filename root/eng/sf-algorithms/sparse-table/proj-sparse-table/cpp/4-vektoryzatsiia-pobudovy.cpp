#include <immintrin.h>
#include <span>
#include <cstddef>
#include <cstdint>
#include <algorithm>

/* Векторизована функція побудови рівня для C++ */
void build_level_avx2(std::span<int32_t> dest, std::span<const int32_t> src, 
                      std::size_t half, std::size_t count) noexcept 
{
    std::size_t i = 0;
    
    for (; i + 8 <= count; i += 8) {
        const __m256i va = _mm256_loadu_si256(reinterpret_cast<const __m256i*>(src.data() + i));
        const __m256i vb = _mm256_loadu_si256(reinterpret_cast<const __m256i*>(src.data() + i + half));
        const __m256i vmin = _mm256_min_epi32(va, vb);
        _mm256_storeu_si256(reinterpret_cast<__m256i*>(dest.data() + i), vmin);
    }
    
    for (; i < count; ++i) {
        dest[i] = std::min(src[i], src[i + half]);
    }
}
