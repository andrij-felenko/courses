#include <stdint.h>
#include <stdbool.h>

/* Застарілий підхід: ручний inline asm для x86 */
bool atomic_compare_exchange_asm(uint32_t *ptr, uint32_t expected, uint32_t desired) {
    uint8_t success;
    __asm__ __volatile__ (
        "lock; cmpxchgl %[desired], %[memory]\n\t"
        "sete %[success]"
        : [memory] "+m" (*ptr),
          [success] "=q" (success),
          "+a" (expected)
        : [desired] "r" (desired)
        : "cc", "memory"
    );
    return success != 0;
}
