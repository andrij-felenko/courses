#include <numeric>    // std::gcd
#include <cstdint>
#include <span>

std::int64_t gcd_all(std::span<const std::int64_t> xs) {
    std::int64_t g = 0;                  // нейтральний елемент: НСД(0, x) = x
    for (std::int64_t x : xs) {
        g = std::gcd(g, x);
        if (g == 1) return 1;            // одиницю вже ніщо не зрушить
    }
    return g;
}
