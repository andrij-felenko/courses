#include <cstdint>
#include <cstddef>
#include <span>
#include <concepts>
#include <type_traits>

namespace ct {

// Перетворення прапорця 0/1 у суцільну маску
template <std::unsigned_integral T>
[[nodiscard]] constexpr T to_mask(T bit) noexcept {
    using SignedT = std::make_signed_t<T>;
    return static_cast<T>(-static_cast<SignedT>(bit & 1));
}

// Безгалузевий вибір між двома значеннями
template <std::unsigned_integral T>
[[nodiscard]] constexpr T select(T mask, T a, T b) noexcept {
    return (a & mask) | (b & ~mask);
}

// Умовне копіювання за константний час
template <typename T>
void conditional_copy(bool flag, std::span<T> dst, std::span<const T> src) noexcept {
    if (dst.size() != src.size()) return;

    const uint8_t mask = static_cast<uint8_t>(-static_cast<int8_t>(flag ? 1 : 0));
    auto* dst_bytes = reinterpret_cast<uint8_t*>(dst.data());
    const auto* src_bytes = reinterpret_cast<const uint8_t*>(src.data());
    const size_t total_bytes = dst.size_bytes();

    for (size_t i = 0; i < total_bytes; ++i) {
        dst_bytes[i] ^= mask & (src_bytes[i] ^ dst_bytes[i]);
    }

    asm volatile("" : : "r"(dst_bytes) : "memory");
}

// Умовний обмін пам'яті двох діапазонів
template <typename T>
void conditional_swap(bool flag, std::span<T> a, std::span<T> b) noexcept {
    if (a.size() != b.size()) return;

    const uint8_t mask = static_cast<uint8_t>(-static_cast<int8_t>(flag ? 1 : 0));
    auto* a_bytes = reinterpret_cast<uint8_t*>(a.data());
    auto* b_bytes = reinterpret_cast<uint8_t*>(b.data());
    const size_t total_bytes = a.size_bytes();

    for (size_t i = 0; i < total_bytes; ++i) {
        const uint8_t delta = mask & (a_bytes[i] ^ b_bytes[i]);
        a_bytes[i] ^= delta;
        b_bytes[i] ^= delta;
    }

    asm volatile("" : : "r"(a_bytes), "r"(b_bytes) : "memory");
}

} // namespace ct
