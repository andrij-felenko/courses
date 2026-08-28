#include <stdint.h>
#include <stddef.h>
#include <tmmintrin.h> /* SSSE3 intrinsics */

/* Векторне перетворення 16 байтів у 32 hex-символи через pshufb */
void hex_encode_16bytes_simd(const uint8_t *src, char *dst) {
    /* Завантажуємо 16 байтів у 128-бітний XMM регістр */
    __m128i input = _mm_loadu_si128((const __m128i *)src);

    /* Таблиця замін ASCII: '0'-'9', 'a'-'f' (16 байтів у регістрі XMM) */
    const __m128i hex_lut = _mm_setr_epi8(
        '0', '1', '2', '3', '4', '5', '6', '7',
        '8', '9', 'a', 'b', 'c', 'd', 'e', 'f'
    );

    __m128i mask_low = _mm_set1_epi8(0x0F);

    /* Виділяємо молодші (low) та старші (high) 4-бітні нібли */
    __m128i low_nibbles  = _mm_and_si128(input, mask_low);
    __m128i high_nibbles = _mm_and_si128(_mm_srli_epi16(input, 4), mask_low);

    /* Паралельна таблична заміна 16 байтів за 1 такт інструкцією pshufb! */
    __m128i hex_chars_low  = _mm_shuffle_epi8(hex_lut, low_nibbles);
    __m128i hex_chars_high = _mm_shuffle_epi8(hex_lut, high_nibbles);

    /* Чергуємо старші та молодші символи для отримання правильного ASCII порядку */
    __m128i result_0_15 = _mm_unpacklo_epi8(hex_chars_high, hex_chars_low);
    __m128i result_16_31 = _mm_unpackhi_epi8(hex_chars_high, hex_chars_low);

    /* Зберігаємо 32 байти готового шістнадцяткового рядка */
    _mm_storeu_si128((__m128i *)dst, result_0_15);
    _mm_storeu_si128((__m128i *)(dst + 16), result_16_31);
}
