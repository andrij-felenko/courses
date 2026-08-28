#include <cstdint>

// Безрозгалужений вибір у константному часі
[[nodiscard]] constexpr uint64_t ct_sub_if_gte(uint64_t t, uint64_t n) noexcept {
    const uint64_t d = t - n;
    // Отримуємо бітову маску через знак запозичення
    const uint64_t borrow = (t < n) ? 1ULL : 0ULL;
    const uint64_t mask = -borrow;
    return (t & mask) | (d & ~mask);
}
