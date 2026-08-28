#include <iostream>
#include <algorithm>

template <typename T>
constexpr T min_func(T a, T b) noexcept {
    return (a < b) ? a : b;
}

int main() {
    int counter = 0;
    int limit = 5;

    auto get_next = [&counter]() { return counter++; };

    // Функція гарантує одиничне обчислення аргументу під час виклику
    int m = min_func(get_next(), limit);

    std::cout << "m = " << m << ", counter = " << counter << " (counter=1)\n";
    return 0;
}
