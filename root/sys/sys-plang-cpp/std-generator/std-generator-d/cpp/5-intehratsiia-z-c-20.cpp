#include <generator>
#include <ranges>
#include <iostream>

// Генератор нескінченної послідовності чисел
std::generator<int> infinite_sequence(int start = 0) {
    while (true) {
        co_yield start++;
    }
}

int main() {
    // Побудова суцільного лінивого конвеєра обробки:
    // 1. Генеруємо нескінченні числа починаючи з 1
    // 2. Фільтруємо лише парні числа (views::filter)
    // 3. Підносимо до квадрата (views::transform)
    // 4. Обмежуємо першими 5 елементами (views::take)
    auto pipeline = infinite_sequence(1)
        | std::views::filter([](int n) { return n % 2 == 0; })
        | std::views::transform([](int n) { return n * n; })
        | std::views::take(5);

    for (int val : pipeline) {
        std::cout << val << " "; // Виводить: 4 16 36 64 100
    }
}
