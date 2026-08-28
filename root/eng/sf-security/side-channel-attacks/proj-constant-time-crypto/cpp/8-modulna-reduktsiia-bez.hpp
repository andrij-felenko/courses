#include <cstdint>
#include <concepts>

namespace crypto::constant_time {

/* Постійночасова редукція Барретта для цілих типів */
template <std::unsigned_integral T, std::unsigned_integral T_Wide>
[[nodiscard]] constexpr T barrett_reduce(T_Wide a, T q, T_Wide mu, int k) noexcept {
    const T_Wide q_hat = (a * mu) >> k;
    T_Wide r = a - q_hat * q;

    const bool is_ge = !is_less(static_cast<T>(r), q);
    const T mask = barrier(static_cast<T>(-static_cast<int32_t>(is_ge ? 1 : 0)));

    r -= static_cast<T_Wide>(mask & q);
    return static_cast<T>(r);
}

} // namespace crypto::constant_time
