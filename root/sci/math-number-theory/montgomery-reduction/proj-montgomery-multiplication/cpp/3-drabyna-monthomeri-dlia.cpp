#include <cstdint>
#include <concepts>

// Модульне піднесення до степеня методом Драбини Монтгомері
[[nodiscard]] uint64_t modular_pow(const Montgomery64& ctx, uint64_t base, uint64_t exp) noexcept {
    const uint64_t x_bar = ctx.to_domain(base);
    
    uint64_t r0 = ctx.r_mod_n(); // Образ 1
    uint64_t r1 = x_bar;         // Образ base
    
    for (int i = 63; i >= 0; --i) {
        const uint64_t bit = (exp >> i) & 1ULL;
        const uint64_t mask = -bit;
        
        // Безрозгалужений умовний обмін (Constant-Time CSwap)
        const uint64_t diff = (r0 ^ r1) & mask;
        r0 ^= diff;
        r1 ^= diff;
        
        r1 = ctx.multiply(r0, r1);
        r0 = ctx.multiply(r0, r0);
        
        const uint64_t back_diff = (r0 ^ r1) & mask;
        r0 ^= back_diff;
        r1 ^= back_diff;
    }
    
    return ctx.from_domain(r0);
}
