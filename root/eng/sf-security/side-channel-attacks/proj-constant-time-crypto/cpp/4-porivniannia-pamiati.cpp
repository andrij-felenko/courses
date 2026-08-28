#include <cstdint>
#include <cstddef>
#include <span>
#include <concepts>

namespace crypto::constant_time {

/* Безпечне порівняння двох послідовностей байтів std::span */
[[nodiscard]] bool are_equal(std::span<const uint8_t> a, std::span<const uint8_t> b) noexcept {
    if (a.size() != b.size()) {
        return false;
    }

    uint8_t diff = 0;
    for (size_t i = 0; i < a.size(); ++i) {
        diff |= (a[i] ^ b[i]);
    }

    const uint32_t acc = diff;
    const uint32_t is_zero = ((acc | static_cast<uint32_t>(-static_cast<int32_t>(acc))) >> 31) ^ 1U;
    return is_zero == 1U;
}

/* Перевірка відношення менше (x < y) без розгалужень */
template <std::unsigned_integral T>
[[nodiscard]] constexpr bool is_less(T x, T y) noexcept {
    const T diff = x ^ y;
    const T sub = x - y;
    const T borrow = (x & ~y) | ((~diff) & sub);
    constexpr size_t shift = (sizeof(T) * 8) - 1;
    return ((borrow >> shift) & static_cast<T>(1)) != static_cast<T>(0);
}

} // namespace crypto::constant_time
