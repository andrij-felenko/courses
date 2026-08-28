#include <cstdint>
#include <utility>

/* Ідіоматична C++ версія, що повертає пару зі значенням і прапорцем */
std::pair<uint64_t, uint8_t> add_with_carry(uint64_t a, uint64_t b) noexcept {
    uint64_t sum = 0;
    uint8_t carry = 0;
    
    asm volatile (
        "addq %[src], %[dst]\n\t"
        "setc %[c_out]"
        : [dst] "=r" (sum),
          [c_out] "=q" (carry)
        : [src] "r" (b),
          "[dst]" (a)
        : "cc"
    );
    
    return {sum, carry};
}
