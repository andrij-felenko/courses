#include <iostream>
#include <type_traits>
#include <vector>

namespace custom {

// Спеціальний тип для позначення невдалої підстановки в інтроспекції
struct nonesuch {
    ~nonesuch() = delete;
    nonesuch(nonesuch const&) = delete;
    void operator=(nonesuch const&) = delete;
};

namespace detail {
template <template <class...> class Op, class AlwaysVoid, class... Args>
struct detector : std::false_type {
    using type = nonesuch;
};

template <template <class...> class Op, class... Args>
struct detector<Op, std::void_t<Op<Args...>>, Args...> : std::true_type {
    using type = Op<Args...>;
};
} // namespace detail

// 1. Метапредикат: чи валідний вираз Op<Args...>?
template <template <class...> class Op, class... Args>
using is_detected = typename detail::detector<Op, void, Args...>::value_type;

template <template <class...> class Op, class... Args>
inline constexpr bool is_detected_v = is_detected<Op, Args...>::value;

// 2. Безпечний витяг типу: повертає Op<Args...> або nonesuch у разі помилки
template <template <class...> class Op, class... Args>
using detected_t = typename detail::detector<Op, void, Args...>::type;

} // namespace custom

// --- Застосування Detection Idiom ---

// Шаблон операції: перевірка наявності вкладеного типу value_type
template<typename T>
using value_type_t = typename T::value_type;

// Шаблон операції: перевірка оператора індексації [size_t]
template<typename T>
using index_operator_t = decltype(std::declval<T>()[std::declval<size_t>()]);

int main() {
    std::cout << std::boolalpha;

    // Перевірка наявності вкладеного typeset value_type
    std::cout << "vector має value_type: " 
              << custom::is_detected_v<value_type_t, std::vector<int>> << "\n"; // true
    std::cout << "int має value_type: " 
              << custom::is_detected_v<value_type_t, int> << "\n";              // false

    // Перевірка наявності оператора []
    std::cout << "vector має operator[]: " 
              << custom::is_detected_v<index_operator_t, std::vector<int>> << "\n"; // true
}
