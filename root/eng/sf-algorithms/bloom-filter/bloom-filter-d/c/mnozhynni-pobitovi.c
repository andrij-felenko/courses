#include <stdint.h>
#include <size_t.h>

/* Векторизоване побітове об'єднання двох фільтрів Блума у C */
void bloom_union_fast(uint8_t *dst, const uint8_t *src, size_t bytes) {
    size_t i = 0;
    /* Ущільнена обробка по 64 біти (8 байтів) за такт */
    for (; i + 7 < bytes; i += 8) {
        uint64_t *d64 = (uint64_t *)&dst[i];
        const uint64_t *s64 = (const uint64_t *)&src[i];
        *d64 |= *s64;
    }
    for (; i < bytes; i++) {
        dst[i] |= src[i];
    }
}
