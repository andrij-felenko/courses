#include <iostream>
#include <vector>
#include <string>
#include <ranges>

int main() {
    std::vector<std::string> names = {"Alice", "Bob", "Charlie"};
    std::vector<int> ids = {101, 102, 103};

    // Композиція zip та enumerate у C++23:
    for (auto [index, tuple_data] : std::views::zip(names, ids) | std::views::enumerate) {
        auto [name, id] = tuple_data;
        std::cout << "#" << index + 1 << ": " << name << " (ID: " << id << ")\n";
    }
    return 0;
}
