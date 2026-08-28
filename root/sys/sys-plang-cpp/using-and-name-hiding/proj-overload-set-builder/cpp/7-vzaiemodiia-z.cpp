#include <concepts>
#include <iostream>
#include <variant>
#include <vector>
#include <string>

template <typename... Ts>
struct Overload : Ts... {
    using Ts::operator()...;
};
template <typename... Ts>
Overload(Ts...) -> Overload<Ts...>;

using DynamicValue = std::variant<int, double, std::string, std::vector<int>>;

void inspect_value(const DynamicValue& val) {
    std::visit(Overload{
        // Спеціалізована обробка для рядків:
        [](const std::string& s) {
            std::cout << "Рядок: \"" << s << "\", довжина: " << s.size() << '\n';
        },
        // Концепт для всіх числових типів (int, double тощо):
        []<std::floating_point T>(T num) {
            std::cout << "Дробове число: " << num << '\n';
        },
        []<std::integral T>(T num) {
            std::cout << "Ціле число: " << num << '\n';
        },
        // Концепт для контейнерів, що підтримують ітерацію:
        []<typename T>(const std::vector<T>& vec) {
            std::cout << "Вектор розміром: " << vec.size() << '\n';
        }
    }, val);
}
