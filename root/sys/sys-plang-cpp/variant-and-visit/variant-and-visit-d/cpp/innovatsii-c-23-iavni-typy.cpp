#include <variant>
#include <string>
#include <string_view>
#include <iostream>

using Value = std::variant<int, std::string>;

int main() {
    Value v1 = 42;
    Value v2 = std::string("Hello World");

    // C++23: Явне вказання типу повернення std::string_view
    auto res1 = std::visit<std::string_view>(overloaded{
        [](int i) -> std::string { return std::to_string(i); },
        [](const std::string& s) -> std::string_view { return s; }
    }, v1);

    std::cout << "Результат 1: " << res1 << "\n";
}
