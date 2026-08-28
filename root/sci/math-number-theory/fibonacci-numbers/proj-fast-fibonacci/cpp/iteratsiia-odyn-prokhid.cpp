#include <cstdint>

std::uint64_t fib_iter(int n) {
    std::uint64_t a = 0, b = 1;          // a = F₀, b = F₁
    for (int i = 0; i < n; ++i) {
        std::uint64_t t = a + b;         // наступний член
        a = b;
        b = t;
    }
    return a;                            // a = Fₙ
}
