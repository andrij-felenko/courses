#include <stdint.h>

/**
 * @brief Константний вибір: повертає a, якщо condition == 1; повертає b, якщо condition == 0.
 * condition має бути строго 0 або 1.
 */
uint32_t ct_select_u32(uint32_t condition, uint32_t a, uint32_t b) {
    // Створюємо маску: якщо condition == 1 -> mask = 0xFFFFFFFF; якщо condition == 0 -> mask = 0x00000000
    uint32_t mask = (uint32_t)(-(int32_t)condition);
    return (mask & a) | (~mask & b);
}
