#include <cstddef>
#include <type_traits>
#include <concepts>

namespace math {

/*
 * Функція часу компіляції (constexpr / consteval).
 * Якщо індекси відомі під час компіляції, результат обчислюється одразу.
 */
[[nodiscard]] constexpr int kronecker_delta(std::size_t i, std::size_t j) noexcept {
    return (i == j) ? 1 : 0;
}

/*
 * Шаблонний варіант для статичних цілочислових констант.
 * Значення генерується як частина типу через std::integral_constant.
 */
template <std::size_t I, std::size_t J>
struct static_kronecker : std::integral_constant<int, (I == J ? 1 : 0)> {};

template <std::size_t I, std::size_t J>
inline constexpr int static_kronecker_v = static_kronecker<I, J>::value;

/*
 * Концепт та безрозгалужений зважений фільтр значень.
 */
template <typename T>
requires std::is_arithmetic_v<T>
[[nodiscard]] constexpr T kronecker_select(std::size_t i, std::size_t j, T val) noexcept {
    return static_cast<T>(i == j) * val;
}

} // namespace math
