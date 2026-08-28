#include <vector>
#include <cstdint>

// Жадібний генератор: формує весь масив у купі
std::vector<std::uint64_t> generate_fibonacci_eager(std::size_t n) {
    std::vector<std::uint64_t> result;
    result.reserve(n);
    
    std::uint64_t a = 0, b = 1;
    for (std::size_t i = 0; i < n; ++i) {
        result.push_back(a);
        auto next = a + b;
        a = b;
        b = next;
    }
    return result; // Копіювання або переміщення цілого вектора
}
