#include <cstdint>

// Зведення числа x за модулем Mp = 2ᵖ − 1 без використання ділення
constexpr std::uint64_t reduce_small(unsigned __int128 x, int p) noexcept {
    const std::uint64_t M = (static_cast<std::uint64_t>(1) << p) - 1;
    while (x >> p) {
        x = (x & M) + (x >> p);
    }
    return (x == M) ? 0 : static_cast<std::uint64_t>(x);
}

// Тест Люка–Лемера для малих p (p ≤ 61, коли Mp вміщується в uint64_t)
constexpr bool lucas_lehmer_small(int p) noexcept {
    if (p == 2) return true;                   // M₂ = 3 — просте число
    if (p < 2 || p > 61) return false;         // межі 64-бітного машинного слова
    const std::uint64_t M = (static_cast<std::uint64_t>(1) << p) - 1;
    std::uint64_t s = 4;                       // початковий член S₀ = 4
    for (int i = 0; i < p - 2; ++i) {
        const unsigned __int128 sq = static_cast<unsigned __int128>(s) * s;
        const std::uint64_t r = reduce_small(sq, p);
        s = (r >= 2) ? r - 2 : r + M - 2;
    }
    return s == 0;                             // Sₚ₋₂ ≡ 0 (mod Mp) ⇔ Mp просте
}
