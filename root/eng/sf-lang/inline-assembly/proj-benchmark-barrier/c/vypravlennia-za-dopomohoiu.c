#include <stdint.h>

/* КОРЕКТНО: модифікатор & гарантує унікальність фізичного регістра */
uint64_t safe_accumulate(uint64_t base, uint64_t multiplier) {
    uint64_t result;
    __asm__ (
        "movq %1, %0\n\t"
        "imulq %2, %0\n\t"
        "addq %1, %0"
        : "=&r" (result)        /* ВИПРАВЛЕНО: earlyclobber захищає від злиття регістрів */
        : "r" (base), "r" (multiplier)
        : "cc"
    );
    return result;
}
