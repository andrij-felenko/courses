#include <immintrin.h>
#include <cstdint>
#include <array>

namespace sys {

// SIMD-векторизоване опитування пакету у C++
void check_batch_avx2(const uint8_t* bits, std::span<const uint64_t, 4> h1,
                      std::span<const uint64_t, 4> h2, std::array<bool, 4>& results) noexcept {
    __m256i v1 = _mm256_loadu_si256(reinterpret_cast<const __m256i*>(h1.data()));
    __m256i v2 = _mm256_loadu_si256(reinterpret_cast<const __m256i*>(h2.data()));
    __m256i v_sum = _mm256_add_epi64(v1, v2);
    alignas(32) std::uint64_t indices[4];
    _mm256_store_si256(reinterpret_cast<__m256i*>(indices), v_sum);

    for (std::size_t i = 0; i < 4; ++i) {
        results[i] = ((bits[indices[i] >> 3] & (1u << (indices[i] & 7))) != 0);
    }
}

} // namespace sys
