#include <iostream>
#include <variant>
#include <string>
#include <concepts>
#include <type_traits>

// Базовий шаблон зі змінною кількістю аргументів (Variadic Template)
template<typename... Ts>
struct Overloaded : Ts... {
    using Ts::operator()...; // Розпакування using-оголошень для всіх базових класів (C++17)
};

// Користувацьке правило виведення (Deduction Guide)
template<typename... Ts>
Overloaded(Ts...) -> Overloaded<Ts...>;
