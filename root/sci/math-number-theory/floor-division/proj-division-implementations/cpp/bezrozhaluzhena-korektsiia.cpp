#include <cstdint>
#include <concepts>
#include <bit>

// C++20 шаблонований безрозгалужений зсув
template <std::signed_integral T>
[[nodiscard]] constexpr T fast_trunc_div_pow2(T a, unsigned int k) noexcept {
    constexpr auto bits = sizeof(T) * 8 - 1;
    const T bias = (a >> bits) & ((static_cast<T>(1) << k) - 1);
    return (a + bias) >> k;
}
