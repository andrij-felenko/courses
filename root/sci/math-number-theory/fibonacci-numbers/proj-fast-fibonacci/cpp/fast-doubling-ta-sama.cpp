#include <cstdint>
#include <bit>            // std::countl_zero — C++20
#include <utility>        // std::pair

// повертає пару (Fₙ, Fₙ₊₁); коректно для n ≤ 93, далі uint64 переповнюється
std::pair<std::uint64_t, std::uint64_t> fib_fast(std::uint64_t n) {
    std::uint64_t a = 0, b = 1;                  // (F₀, F₁)
    for (int i = 63 - std::countl_zero(n | 1); i >= 0; --i) {
        std::uint64_t c = a * (2 * b - a);       // F(2k)   = Fₖ·(2Fₖ₊₁ − Fₖ)
        std::uint64_t d = a * a + b * b;         // F(2k+1) = Fₖ₊₁² + Fₖ²
        if ((n >> i) & 1) { a = d; b = c + d; }  // розряд = 1: ще крок уперед
        else              { a = c; b = d;     }  // розряд = 0
    }
    return {a, b};
}
