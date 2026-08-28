#include <cstdint>
#include <bit>
#include <immintrin>
#include <span>

/* Варіант C++20: стандартний алгоритм транслюється прямо в intrinsic */
constexpr int count_leading_zeros_modern(uint32_t val) noexcept {
    return std::countl_zero(val); /* Може обчислюватися під час компіляції (constexpr) */
}

/* Ідіоматична робота з SIMD через intrinsics у C++ */
void add_vectors_sse(std::span<const float, 4> a, 
                     std::span<const float, 4> b, 
                     std::span<float, 4> result) noexcept {
    const __m128 va = _mm_loadu_ps(a.data());
    const __m128 vb = _mm_loadu_ps(b.data());
    const __m128 vres = _mm_add_ps(va, vb);
    _mm_storeu_ps(result.data(), vres);
}
