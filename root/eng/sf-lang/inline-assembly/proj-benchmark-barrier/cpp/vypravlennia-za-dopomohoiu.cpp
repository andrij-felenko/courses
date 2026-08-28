#include <cstdint>

/* КОРЕКТНИЙ ідіоматичний C++ код */
uint64_t safe_accumulate(uint64_t base, uint64_t multiplier) noexcept {
    uint64_t result = 0;
    asm (
        "movq %1, %0\n\t"
        "imulq %2, %0\n\t"
        "addq %1, %0"
        : "=&r" (result)        /* ВИПРАВЛЕНО: earlyclobber */
        : "r" (base), "r" (multiplier)
        : "cc"
    );
    return result;
}
