#include <immintrin.h>
#include <bit>
#include <array>

// Стандарто-сумісна обробка SIMD векторів у C++20
std::array<float, 4> extract_floats_safe(__m128 vec) noexcept {
    // std::bit_cast гарантовано і безпечно переносить біти у std::array
    return std::bit_cast<std::array<float, 4>>(vec);
}

__m128i mask_float_vector(__m128 vf) noexcept {
    // Для процесорних векторів _mm_castps_si128 залишається ідіоматичним нуль-вартісним кастом
    const auto vi = _mm_castps_si128(vf);
    const auto mask = _mm_set1_epi32(0x7FFFFFFF);
    return _mm_and_si128(vi, mask);
}
