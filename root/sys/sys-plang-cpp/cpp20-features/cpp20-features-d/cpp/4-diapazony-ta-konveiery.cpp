#include <iostream>
#include <vector>
#include <ranges>

int main() {
    std::vector<int> numbers = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10};

    // Конвеєр: відібрати парні, піднести до квадрата, взяти перші три
    auto pipeline = numbers
                  | std::views::filter([](int n) { return n % 2 == 0; })
                  | std::views::transform([](int n) { return n * n; })
                  | std::views::take(3);

    for (int value : pipeline) {
        std::cout << value << " "; // Виведе: 4 16 36
    }
    return 0;
}
