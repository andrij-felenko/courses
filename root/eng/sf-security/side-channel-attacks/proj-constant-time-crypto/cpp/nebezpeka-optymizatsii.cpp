#include <cstdint>
#include <cstddef>
#include <span>
#include <array>
#include <concepts>

namespace crypto::constant_time {

/* Асемблерний бар'єр для захисту від шкідливих компіляторних перетворень */
template <std::unsigned_integral T>
[[nodiscard]] constexpr T barrier(T val) noexcept {
    #if defined(__GNUC__) || defined(__clang__)
    asm volatile ("" : "+r" (val));
    #endif
    return val;
}

/* Типобезпечний умовний вибір для довільних беззнакових цілих типів */
template <std::unsigned_integral T>
[[nodiscard]] constexpr T select(bool condition, T x, T y) noexcept {
    const T cond_val = condition ? static_cast<T>(1) : static_cast<T>(0);
    const T mask = barrier(static_cast<T>(-static_cast<T>(cond_val)));
    return y ^ (mask & (x ^ y));
}

/* Умовне оновлення діапазону пам'яті std::span */
void select_span(bool condition, std::span<uint8_t> dst, std::span<const uint8_t> src) noexcept {
    if (dst.size() != src.size()) {
        return;
    }
    const uint8_t cond_val = condition ? 1U : 0U;
    const uint8_t mask = barrier(static_cast<uint8_t>(-static_cast<int8_t>(cond_val)));
    for (size_t i = 0; i < dst.size(); ++i) {
        dst[i] ^= mask & (src[i] ^ dst[i]);
    }
}

} // namespace crypto::constant_time
