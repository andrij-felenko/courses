#include <cstdint>
#include <array>
#include <span>
#include <immintrin.h>

class FastHexEncoder {
public:
    static void encode_block_16(std::span<const uint8_t, 16> src, std::span<char, 32> dst) noexcept {
        const __m128i input = _mm_loadu_si128(reinterpret_cast<const __m128i*>(src.data()));

        const __m128i hex_lut = _mm_setr_epi8(
            '0', '1', '2', '3', '4', '5', '6', '7',
            '8', '9', 'a', 'b', 'c', 'd', 'e', 'f'
        );
        const __m128i mask_low = _mm_set1_epi8(0x0F);

        const __m128i low_nibbles  = _mm_and_si128(input, mask_low);
        const __m128i high_nibbles = _mm_and_si128(_mm_srli_epi16(input, 4), mask_low);

        const __m128i hex_low  = _mm_shuffle_epi8(hex_lut, low_nibbles);
        const __m128i hex_high = _mm_shuffle_epi8(hex_lut, high_nibbles);

        const __m128i res_part1 = _mm_unpacklo_epi8(hex_high, hex_low);
        const __m128i res_part2 = _mm_unpackhi_epi8(hex_high, hex_low);

        _mm_storeu_si128(reinterpret_cast<__m128i*>(dst.data()), res_part1);
        _mm_storeu_si128(reinterpret_cast<__m128i*>(dst.data() + 16), res_part2);
    }
};
