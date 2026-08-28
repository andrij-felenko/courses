#include <stdint.h>

/* Безпечний умовний вибір постійного часу:
   Повертає a, якщо condition == 1, інакше b */
uint32_t ct_select_u32(uint32_t condition, uint32_t a, uint32_t b) {
    uint32_t mask = -(condition);
    #if defined(__GNUC__) || defined(__clang__)
    __asm__ volatile ("" : "+r" (mask));
    #endif
    return b ^ (mask & (a ^ b));
}
