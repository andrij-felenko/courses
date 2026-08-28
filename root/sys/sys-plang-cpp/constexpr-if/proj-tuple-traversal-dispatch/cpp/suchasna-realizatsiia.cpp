#include <iostream>
#include <tuple>
#include <string>
#include <type_traits>
#include <utility>

namespace detail {

template<std::size_t Index = 0, typename Func, typename... Types>
constexpr void tuple_for_each_impl(const std::tuple<Types...>& t, Func&& f) {
    constexpr std::size_t total_elements = sizeof...(Types);

    if constexpr (Index < total_elements) {
        // 1. Обробляємо поточний елемент кортежу
        f(std::get<Index>(t), Index);

        // 2. Рекурсивний перехід до наступного елемента
        // Якщо Index + 1 == total_elements, ця гілка ВІДКИДАЄТЬСЯ компілятором!
        if constexpr (Index + 1 < total_elements) {
            tuple_for_each_impl<Index + 1>(t, std::forward<Func>(f));
        }
    }
}

} // namespace detail

template<typename Func, typename... Types>
constexpr void tuple_for_each(const std::tuple<Types...>& t, Func&& f) {
    detail::tuple_for_each_impl<0>(t, std::forward<Func>(f));
}
