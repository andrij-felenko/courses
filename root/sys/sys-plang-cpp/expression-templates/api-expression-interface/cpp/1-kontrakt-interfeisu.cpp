#include <type_traits>
#include <cstddef>
#include <concepts>

// Концепт C++20, що формалізує вимоги до векторного виразу
template <typename T>
concept VectorExpression = requires(const T& expr, std::size_t i) {
    typename T::value_type;
    { expr.size() } -> std::same_as<std::size_t>;
    { expr[i] }     -> std::convertible_to<typename T::value_type>;
};
