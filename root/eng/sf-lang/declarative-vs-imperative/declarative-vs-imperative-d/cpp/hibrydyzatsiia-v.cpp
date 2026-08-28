#include <vector>
#include <string>
#include <ranges>
#include <iostream>

struct User {
    std::string name;
    int age;
    bool is_active;
};

void print_active_adult_names(const std::vector<User>& users) {
    // Декларативний конвеєр C++20: композиція операторів через пайп '|'
    auto active_adults = users
        | std::views::filter([](const User& u) { return u.is_active && u.age >= 18; })
        | std::views::transform([](const User& u) { return u.name; })
        | std::views::take(5);

    for (const auto& name : active_adults) {
        std::cout << name << '\n';
    }
}
