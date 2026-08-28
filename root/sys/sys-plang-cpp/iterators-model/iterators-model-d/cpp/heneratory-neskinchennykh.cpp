#include <iostream>
#include <ranges>

int main() {
    // Генерація числа від 1 до нескінченності без створення вектора
    auto infinite_range = std::views::iota(1);

    // Взяти перші 5 елементів і надрукувати
    for (int val : infinite_range | std::views::take(5)) {
        std::cout << val << " "; // 1 2 3 4 5
    }
}
