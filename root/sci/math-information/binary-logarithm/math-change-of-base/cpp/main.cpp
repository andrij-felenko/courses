#include <cmath>
#include <cstdint>

// ✗ Перехід між основами просто в коді: два округлені ірраціональні числа й ділення
double log2_via_ln(std::uint64_t n) {
    return std::log(static_cast<double>(n)) / std::log(2.0);
}
// n = 2²⁹ → 29.000000000000004 → std::ceil(…) → 30, зайвий біт

// ✓ Виділена функція: ділення немає, отже немає й зайвого округлення
double log2_direct(std::uint64_t n) {
    return std::log2(static_cast<double>(n));
}
// n = 2²⁹ → рівно 29.0 → std::ceil(…) → 29
