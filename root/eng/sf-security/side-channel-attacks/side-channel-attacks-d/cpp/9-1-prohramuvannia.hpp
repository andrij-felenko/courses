#include <cstdint>
#include <concepts>

namespace crypto::constant_time {

/* Постійночасовий вибір значення для цілих типів */
template <std::unsigned_integral T>
[[nodiscard]] constexpr T select(bool condition, T a, T b) noexcept {
    const T cond_val = condition ? static_cast<T>(1) : static_cast<T>(0);
    T mask = static_cast<T>(-static_cast<T>(cond_val));
    #if defined(__GNUC__) || defined(__clang__)
    asm volatile ("" : "+r" (mask));
    #endif
    return b ^ (mask & (a ^ b));
}

} // namespace crypto::constant_time
