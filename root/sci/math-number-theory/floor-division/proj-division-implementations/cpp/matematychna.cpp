#include <cstdint>
#include <cstddef>
#include <stdexcept>
#include <concepts>

// Ідіоматичний C++20 шаблонний алгоритм із концептами
template <std::unsigned_integral T>
[[nodiscard]] constexpr T safe_ceil_div(T a, T b) {
    if (b == 0) {
        throw std::invalid_argument("Division by zero in safe_ceil_div");
    }
    if (a == 0) return 0;
    
    // Безпечне обчислення без арифметичного переповнення
    return static_cast<T>(1) + (a - static_cast<T>(1)) / b;
}
