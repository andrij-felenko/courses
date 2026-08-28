#include <bit>

namespace std {
    template <typename T>
    [[nodiscard]] constexpr int popcount(T x) noexcept;

    template <typename T>
    [[nodiscard]] constexpr bool has_single_bit(T x) noexcept;

    template <typename T>
    [[nodiscard]] constexpr T bit_ceil(T x);

    template <typename T>
    [[nodiscard]] constexpr T bit_floor(T x) noexcept;

    template <typename T>
    [[nodiscard]] constexpr int bit_width(T x) noexcept;

    template <typename T>
    [[nodiscard]] constexpr int countl_zero(T x) noexcept;

    template <typename T>
    [[nodiscard]] constexpr int countr_zero(T x) noexcept;

    template <typename T>
    [[nodiscard]] constexpr int countl_one(T x) noexcept;

    template <typename T>
    [[nodiscard]] constexpr int countr_one(T x) noexcept;
}
