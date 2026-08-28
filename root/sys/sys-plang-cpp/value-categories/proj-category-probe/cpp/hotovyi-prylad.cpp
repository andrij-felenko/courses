#include <cstdio>
#include <string>
#include <utility>
#include "value_category_probe.hpp"

// Нічого з цього не треба ВИЗНАЧАТИ: жоден вираз нижче не виконується
std::string          make();
extern std::string   s;
extern std::string&& r;

int main() {
    std::puts(VALUE_CATEGORY(s));             // lvalue
    std::puts(VALUE_CATEGORY(r));             // lvalue  ← має ім'я
    std::puts(VALUE_CATEGORY(std::move(s)));  // xvalue
    std::puts(VALUE_CATEGORY(make()));        // prvalue
}
