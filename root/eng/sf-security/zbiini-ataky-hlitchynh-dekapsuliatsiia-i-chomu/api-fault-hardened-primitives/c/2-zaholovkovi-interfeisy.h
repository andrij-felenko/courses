#ifndef HARDENED_PRIMITIVES_H
#define HARDENED_PRIMITIVES_H

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef uint32_t hardened_bool_t;
typedef uint32_t hardened_status_t;

#define HARDENED_TRUE            ((hardened_bool_t)0x5555AAAAU)
#define HARDENED_FALSE           ((hardened_bool_t)0xAAAA5555U)
#define HARDENED_INVALID         ((hardened_bool_t)0x00000000U)
#define HARDENED_FAULT           ((hardened_bool_t)0xFFFFFFFFU)

#define HARDENED_STATUS_OK       ((hardened_status_t)0x3C3C5A5AU)
#define HARDENED_STATUS_ERROR    ((hardened_status_t)0xC3C3A5A5U)

/**
 * @brief Асемблерний бар'єр оптимізації компілятора.
 * Запобігає об'єднанню або видаленню повторних перевірок компілятором.
 */
#define HARDENED_BARRIER()       __asm__ volatile("" ::: "memory")

/**
 * @brief Безпечне порівняння двох 32-бітних величин на строгу рівність.
 * @param a Перший операнд.
 * @param b Другий операнд.
 * @return HARDENED_TRUE у разі рівності, інакше HARDENED_FALSE.
 */
static inline hardened_bool_t hardened_equal(uint32_t a, uint32_t b) {
    HARDENED_BARRIER();
    uint32_t diff = a ^ b;
    HARDENED_BARRIER();
    
    /* Подвійна перевірка з прямим та комплементарним обчисленням */
    if (diff == 0U) {
        HARDENED_BARRIER();
        if ((a ^ ~b) == 0xFFFFFFFFU) {
            return HARDENED_TRUE;
        }
    }
    return HARDENED_FALSE;
}

/**
 * @brief Перевірка відмовостійкого статусу на відповідність значенню УСПІХ.
 * @param val Перевірюваний статус.
 * @return HARDENED_TRUE якщо статус валідний, інакше HARDENED_FALSE.
 */
static inline hardened_bool_t hardened_verify_success(hardened_status_t val) {
    HARDENED_BARRIER();
    if (val == HARDENED_STATUS_OK) {
        HARDENED_BARRIER();
        if ((val ^ ~HARDENED_STATUS_OK) == 0xFFFFFFFFU) {
            return HARDENED_TRUE;
        }
    }
    return HARDENED_FALSE;
}

/**
 * @brief Негайне блокування пристрою при виявленні невідповідності інваріантів.
 */
void hardened_panic_lockout(void);

#ifdef __cplusplus
}
#endif

#endif /* HARDENED_PRIMITIVES_H */
