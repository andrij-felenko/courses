#include <immintrin.h>
#include <cstdint>
#include <cstddef>
#include <span>

// Ідіоматична C++20 SIMD векторизація ділення масиву на 10
void vec_div10_avx2(std::span<const std::uint32_t> src, std::span<std::uint32_t> dst) noexcept {
    const std::size_t count = src.size();
    std::size_t i = 0;
    const __m256i multiplier = _mm256_set1_epi64x(0xCCCCCCCDULL);
    
    for (; i + 7 < count; i += 8) {
        const __m256i v = _mm256_loadu_si256(reinterpret_cast<const __m256i*>(src.data() + i));
        
        const __m256i prod_even = _mm256_mul_epu32(v, multiplier);
        const __m256i q_even = _mm256_srli_epi64(prod_even, 35);
        
        const __m256i v_odd = _mm256_srli_epi64(v, 32);
        const __m256i prod_odd = _mm256_mul_epu32(v_odd, multiplier);
        const __m256i q_odd = _mm256_srli_epi64(prod_odd, 35);
        
        const __m256i res = _mm256_or_si256(q_even, _mm256_slli_epi64(q_odd, 32));
        
        _mm256_storeu_si256(reinterpret_cast<__m256i*>(dst.data() + i), res);
    }
    
    for (; i < count; ++i) {
        dst[i] = src[i] / 10U;
    }
}
