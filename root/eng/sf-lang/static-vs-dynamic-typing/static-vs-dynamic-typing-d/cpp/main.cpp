#include <iostream>
#include <string>
#include <variant>
#include <any>
#include <vector>

// 1. Безпечний закритий поліморфізм через std::variant (C++17)
using SafeDynamicValue = std::variant<int, double, std::string>;

void process_variant(const SafeDynamicValue& val) {
    std::visit([](const auto& arg) {
        std::cout << "Значення: " << arg << '\n';
    }, val);
}

// 2. Повністю відкритий динамічний тип через std::any (аналог Object у C# / Java)
void process_any(const std::any& val) {
    if (val.type() == typeid(int)) {
        std::cout << "std::any містить int: " << std::any_cast<int>(val) << '\n';
    } else if (val.type() == typeid(std::string)) {
        std::cout << "std::any містить string: " << std::any_cast<std::string>(val) << '\n';
    }
}

int main() {
    SafeDynamicValue v1 = 42;
    SafeDynamicValue v2 = std::string("C++ Variant");
    process_variant(v1);
    process_variant(v2);

    std::any a1 = 1000;
    std::any a2 = std::string("C++ Any");
    process_any(a1);
    process_any(a2);

    return 0;
}
