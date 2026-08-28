#include <variant>
#include <iostream>
#include <string>

// Ідіома Overloaded: об'єднання декількох лямбда-функцій у єдиний структурований відвідувач
template <typename... Ts>
struct overloaded : Ts... {
    using Ts::operator()...;
};

// Deduction guide для C++17
template <typename... Ts>
overloaded(Ts...) -> overloaded<Ts...>;

using DataPayload = std::variant<int, double, std::string>;

void process_payload(const DataPayload& payload) {
    std::visit(overloaded{
        [](int i) { std::cout << "Обробка цілого числа: " << i * 2 << "\n"; },
        [](double d) { std::cout << "Обробка Дійсного числа: " << d / 2.0 << "\n"; },
        [](const std::string& s) { std::cout << "Обробка рядка довжиною: " << s.length() << "\n"; }
    }, payload);
}
