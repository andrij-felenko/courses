#include <bit>        // std::countr_zero — C++20
#include <cstdint>
#include <utility>    // std::swap

std::uint64_t binary_gcd(std::uint64_t u, std::uint64_t v) {
    if (u == 0) return v;
    if (v == 0) return u;

    // Спільні двійки — єдине місце, де НСД їх набирає. Знімаємо і запам'ятовуємо.
    const int k = std::countr_zero(u | v);
    u >>= std::countr_zero(u);           // далі u завжди непарне

    do {
        v >>= std::countr_zero(v);       // робимо непарним і v
        if (u > v) std::swap(u, v);      // тримаємо u ≤ v
        v -= u;                          // різниця двох непарних — парна
    } while (v != 0);

    return u << k;                       // повертаємо спільні двійки на місце
}
