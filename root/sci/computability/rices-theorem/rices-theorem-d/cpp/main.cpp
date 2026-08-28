#include <concepts>

// Варіант A: пряме додавання
constexpr int compute_a(int x) noexcept {
    return x + x;
}

// Варіант B: цикл з акумулятором
constexpr int compute_b(int x) noexcept {
    int sum = 0;
    for (int i = 0; i < x; ++i) {
        sum += 2;
    }
    return sum;
}
