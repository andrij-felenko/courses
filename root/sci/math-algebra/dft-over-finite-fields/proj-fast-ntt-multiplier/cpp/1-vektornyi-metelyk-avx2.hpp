#include <immintrin.h>
#include <span>
#include <cstdint>
#include <cstddef>

void butterfly_avx2(std::span<uint32_t> a, size_t j, size_t t, __m256i mod_vec) noexcept {
    const auto u = _mm256_loadu_si256(reinterpret_cast<const __m256i*>(&a[j]));
    const auto v = _mm256_loadu_si256(reinterpret_cast<const __m256i*>(&a[j + t]));

    /* Поелементне модульне додавання u + v mod p */
    const auto sum = _mm256_add_epi32(u, v);
    const auto mask_sum = _mm256_cmpgt_epi32(sum, mod_vec);
    const auto res_add = _mm256_sub_epi32(sum, _mm256_and_si256(mask_sum, mod_vec));

    /* Модульне віднімання з додаванням константи модуля */
    const auto diff = _mm256_sub_epi32(_mm256_add_epi32(u, mod_vec), v);
    const auto mask_diff = _mm256_cmpgt_epi32(diff, mod_vec);
    const auto res_sub = _mm256_sub_epi32(diff, _mm256_and_si256(mask_diff, mod_vec));

    _mm256_storeu_si256(reinterpret_cast<__m256i*>(&a[j]), res_add);
    _mm256_storeu_si256(reinterpret_cast<__m256i*>(&a[j + t]), res_sub);
}
