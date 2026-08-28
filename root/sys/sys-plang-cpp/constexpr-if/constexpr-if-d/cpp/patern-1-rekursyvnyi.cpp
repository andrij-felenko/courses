#include <tuple>
#include <iostream>
#include <utility>

namespace detail {

template<std::size_t Index = 0, typename Func, typename... Types>
constexpr void for_each_tuple_impl(const std::tuple<Types...>& t, Func&& f) {
    constexpr std::size_t total = sizeof...(Types);

    if constexpr (Index < total) {
        // 1. Викликаємо функцію для поточного елемента
        f(std::get<Index>(t), Index);

        // 2. Рекурсивний перехід до наступного елемента
        // Коли Index + 1 == total, ця гілка ВІДКИДАЄТЬСЯ компілятором!
        if constexpr (Index + 1 < total) {
            for_each_tuple_impl<Index + 1>(t, std::forward<Func>(f));
        }
    }
}

} // namespace detail

template<typename Func, typename... Types>
constexpr void for_each_tuple(const std::tuple<Types...>& t, Func&& f) {
    detail::for_each_tuple_impl<0>(t, std::forward<Func>(f));
}
