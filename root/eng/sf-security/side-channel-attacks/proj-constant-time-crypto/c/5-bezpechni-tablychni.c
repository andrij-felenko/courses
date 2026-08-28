#include <stdint.h>
#include <stddef.h>

/* Безпечна вибірка елемента з 256-байтної таблиці без залежності адреси від секрету */
uint8_t ct_lookup_u8_table256(const uint8_t *table, uint8_t secret_index) {
    uint8_t result = 0;
    for (size_t i = 0; i < 256; ++i) {
        /* Обчислюємо маску: 0xFF якщо i == secret_index, інакше 0x00 */
        uint8_t diff = (uint8_t)(i ^ secret_index);
        uint32_t mask32 = ((uint32_t)diff | (uint32_t)(-(int32_t)diff)) >> 31;
        uint8_t match_mask = (uint8_t)((mask32 ^ 1U) * 0xFFU);

        #if defined(__GNUC__) || defined(__clang__)
        __asm__ volatile ("" : "+r" (match_mask));
        #endif

        result |= match_mask & table[i];
    }
    return result;
}

/* Безпечна вибірка 32-бітного слова з масиву розміром 16 елементів (наприклад, T-таблиці) */
uint32_t ct_lookup_u32_array16(const uint32_t *table, uint32_t secret_index) {
    uint32_t result = 0;
    for (uint32_t i = 0; i < 16; ++i) {
        uint32_t diff = i ^ secret_index;
        uint32_t is_match = ((diff | (uint32_t)(-(int32_t)diff)) >> 31) ^ 1U;
        uint32_t mask = -is_match;

        #if defined(__GNUC__) || defined(__clang__)
        __asm__ volatile ("" : "+r" (mask));
        #endif

        result |= mask & table[i];
    }
    return result;
}
