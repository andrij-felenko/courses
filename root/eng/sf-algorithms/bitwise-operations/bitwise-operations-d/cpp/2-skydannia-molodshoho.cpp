#include <cstdint>
#include <bit>

// Алгоритм Кернігана (якщо немає апаратної інструкції)
[[nodiscard]] constexpr int count_set_bits_fallback(std::uint64_t x) noexcept {
    int count = 0;
    while (x != 0) {
        x &= (x - 1U);
        ++count;
    }
    return count;
}

// Сучасний C++20 використовує апаратну інструкцію процесора (POPCNT)
[[nodiscard]] constexpr int count_set_bits_fast(std::uint64_t x) noexcept {
    return std::popcount(x);
}
