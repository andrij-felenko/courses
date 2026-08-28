#include <iostream>
#include <string>
#include <string_view>

using namespace std::string_literals;      // Для суфікса "s"
using namespace std::string_view_literals; // Для суфікса "sv"

void literals_demo() {
    // 1. Звичайний C-строковий літерал: тип const char[12]
    auto c_str_lit = "Hello World"; 

    // 2. Стандартний рядок std::string: суфікс "s"
    auto str_obj = "Hello World"s; // Тип: std::string

    // 3. Погляд std::string_view: суфікс "sv"
    auto sv_obj = "Hello World"sv; // Тип: std::string_view

    // Перевага "sv": розмір обчислюється під час компіляції (constexpr O(1)), без strlen!
    static_assert(sv_obj.size() == 11);
}
