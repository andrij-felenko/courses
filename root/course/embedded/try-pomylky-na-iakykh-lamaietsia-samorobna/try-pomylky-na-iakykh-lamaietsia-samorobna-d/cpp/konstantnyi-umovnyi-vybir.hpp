#include <cstdint>
#include <type_traits>

/**
 * @brief Константний вибір без розгалужень (C++).
 */
template <typename T>
[[nodiscard]] constexpr T ct_select(bool condition, T a, T b) noexcept {
    static_assert(std::is_integral_v<T>, "Потрібен цілочисельний тип");
    const auto mask = static_cast<T>(-static_cast<std::int64_t>(condition));
    return static_cast<T>((mask & a) | (~mask & b));
}
