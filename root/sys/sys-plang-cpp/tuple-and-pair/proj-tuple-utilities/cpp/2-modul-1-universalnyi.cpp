#include <iostream>
#include <tuple>
#include <string>
#include <utility>

// Допоміжна функція розпакування за допомогою index_sequence
template <typename Tuple, std::size_t... Is>
void print_tuple_impl(std::ostream& os, const Tuple& t, std::index_sequence<Is...>) {
    os << "(";
    // Згортання виразу через оператор кому для друку розділювача ", "
    std::size_t n = 0;
    ((os << (n++ > 0 ? ", " : "") << std::get<Is>(t)), ...);
    os << ")";
}

// Загальний оператор виводу для будь-якого std::tuple
template <typename... Args>
std::ostream& operator<<(std::ostream& os, const std::tuple<Args...>& t) {
    print_tuple_impl(os, t, std::make_index_sequence<sizeof...(Args)>{});
    return os;
}

// Загальний оператор виводу для std::pair
template <typename T1, typename T2>
std::ostream& operator<<(std::ostream& os, const std::pair<T1, T2>& p) {
    return os << "{" << p.first << ", " << p.second << "}";
}
