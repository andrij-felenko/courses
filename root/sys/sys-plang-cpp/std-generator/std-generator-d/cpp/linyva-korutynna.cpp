#include <generator>
#include <cstdint>

// Лінивий корутинний генератор C++23
std::generator<std::uint64_t> generate_fibonacci_lazy() {
    std::uint64_t a = 0, b = 1;
    while (true) {
        co_yield a; // Зупинка корутини та повернення значення 'a'
        auto next = a + b;
        a = b;
        b = next;
    }
}
