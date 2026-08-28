#include <tuple>
#include <utility>
#include <string>
#include <type_traits>

namespace detail {
    template <typename Tuple, typename Func, std::size_t... Is>
    constexpr auto tuple_transform_impl(Tuple&& t, Func&& f, std::index_sequence<Is...>) {
        // Конструювання нового tuple із викликами f(std::get<Is>(t))
        return std::make_tuple(f(std::get<Is>(std::forward<Tuple>(t)))...);
    }
}

// Публічна функція tuple_transform
template <typename Tuple, typename Func>
constexpr auto tuple_transform(Tuple&& t, Func&& f) {
    constexpr std::size_t Size = std::tuple_size_v<std::decay_t<Tuple>>;
    return detail::tuple_transform_impl(
        std::forward<Tuple>(t),
        std::forward<Func>(f),
        std::make_index_sequence<Size>{}
    );
}
