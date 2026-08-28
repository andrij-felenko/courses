#include <iostream>
#include <random>

int main() {
    std::mt19937 rng(42);
    std::uniform_int_distribution<int> dist(1, 10);

    // Отримання поточних параметрів
    auto p1 = dist.param();
    std::cout << "Початковий діапазон: [" << p1.a() << ", " << p1.b() << "]\n";

    // Зміна параметрів через param_type без створення нового розподілу
    using param_t = std::uniform_int_distribution<int>::param_type;
    dist.param(param_t(50, 100));

    std::cout << "Нове значення у діапазоні [50, 100]: " << dist(rng) << "\n";
    return 0;
}
