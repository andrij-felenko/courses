#include <stdint.h>

/* Безпечна модульна редукція за модулем q (для q < 2^15) за алгоритмом Барретта */
uint16_t ct_barrett_reduce_u16(uint32_t a, uint16_t q, uint32_t mu, int k) {
    /* Оцінка частки: quotient ≈ ⌊a / q⌋ */
    uint32_t q_hat = (uint32_t)(((uint64_t)a * mu) >> k);
    uint32_t r = a - q_hat * q;

    /* Корекція: якщо r >= q, віднімаємо q без умовного розгалуження */
    uint32_t is_ge = ct_is_less_u32(r, q) ^ 1U;
    uint32_t mask = -is_ge;

    #if defined(__GNUC__) || defined(__clang__)
    __asm__ volatile ("" : "+r" (mask));
    #endif

    r -= mask & q;
    return (uint16_t)r;
}
