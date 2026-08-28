#include <stdint.h>

uint64_t add_with_carry(uint64_t a, uint64_t b, uint8_t *carry_out) {
    uint64_t sum;
    uint8_t carry;
    
    __asm__ __volatile__ (
        "addq %[src], %[dst]\n\t"   /* Додавання: dst = dst + src */
        "setc %[c_out]"             /* Запис прапорця Carry у змінну */
        : [dst] "=r" (sum),         /* Вихід 0: результат суми */
          [c_out] "=q" (carry)      /* Вихід 1: прапорець переносу (8-бітний регістр) */
        : [src] "r" (b),            /* Вхід 0: доданок b */
          "[dst]" (a)               /* Вхід 1: початкове значення для dst (збігається з sum) */
        : "cc"                      /* Clobber: змінено арифметичні прапорці */
    );
    
    *carry_out = carry;
    return sum;
}
