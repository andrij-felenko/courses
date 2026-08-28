#include <variant>
#include <iostream>

template <typename... Ts>
struct Overload : Ts... {
    using Ts::operator()...; // Розгортає operator() для кожного типу в пакеті Ts
};

// Deduction guide (автоматичне виведення типів аргументів конструктора):
template <typename... Ts>
Overload(Ts...) -> Overload<Ts...>;

void dispatch(const std::variant<int, double, std::string>& val) {
    std::visit(Overload{
        [](int v) { std::cout << "Ціле число: " << v << '\n'; },
        [](double v) { std::cout << "Дробове число: " << v << '\n'; },
        [](const std::string& v) { std::cout << "Рядок: " << v << '\n'; }
    }, val);
}
