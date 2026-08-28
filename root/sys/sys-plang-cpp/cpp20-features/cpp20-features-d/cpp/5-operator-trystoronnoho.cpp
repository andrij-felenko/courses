#include <compare>
#include <string>

struct Employee {
    int id;
    std::string surname;
    double salary;

    // Компілятор почленно порівнює поля у порядку їхнього оголошення
    auto operator<=>(const Employee&) const = default;
};
