#include <iostream>
#include <vector>
#include <ranges>

int main() {
    std::vector<int> numbers = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10};

    // Створення конвеєра обробки даних через оператор pipe |
    auto results = numbers 
                 | std::views::filter([](int n) { return n % 2 == 0; })
                 | std::views::transform([](int n) { return n * n; })
                 | std::views::take(3);

    // Ітерація виконується ледачо (lazy evaluation)!
    for (int val : results) {
        std::cout << val << " "; // Надрукує: 4 16 36
    }
}
