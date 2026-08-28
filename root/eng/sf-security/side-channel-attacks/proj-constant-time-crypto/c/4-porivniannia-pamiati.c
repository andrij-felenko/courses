#include <stdint.h>
#include <stddef.h>

/* Безпечне порівняння двох блоків пам'яті.
   Повертає 0, якщо блоки повністю ідентичні, та 1, якщо є хоча б одна відмінність.
   Час роботи строго пропорційний довжині len і не залежить від вмісту. */
int ct_memcmp(const void *a, const void *b, size_t len) {
    const uint8_t *pa = (const uint8_t *)a;
    const uint8_t *pb = (const uint8_t *)b;
    uint8_t diff = 0;

    for (size_t i = 0; i < len; ++i) {
        diff |= pa[i] ^ pb[i];
    }

    /* Згортання 8-бітного diff: якщо diff != 0, молодший біт результату стає 1.
       Вираз (-(int32_t)diff) генерує від'ємне число для будь-якого diff != 0,
       встановлюючи знаковий біт (31-й біт) в одиницю. */
    uint32_t acc = diff;
    acc = (acc | (uint32_t)(-(int32_t)acc)) >> 31;
    return (int)acc;
}

/* Перевірка на рівність двох чисел: повертає 1, якщо x == y, інакше 0 */
uint32_t ct_is_equal_u32(uint32_t x, uint32_t y) {
    uint32_t diff = x ^ y;
    return ((diff | (uint32_t)(-(int32_t)diff)) >> 31) ^ 1U;
}

/* Перевірка на менше: повертає 1, якщо x < y, інакше 0 */
uint32_t ct_is_less_u32(uint32_t x, uint32_t y) {
    /* x < y <=> різниця x - y генерує позику, або старші знакові біти відрізняються */
    uint32_t diff = x ^ y;
    uint32_t sub = x - y;
    uint32_t borrow = (x & ~y) | ((~diff) & sub);
    return (borrow >> 31) & 1U;
}
