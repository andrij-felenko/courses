// Динамічне програмування мовою C++: ідіоматичний контейнер std::vector
#include <vector>
#include <cstdint>
#include <stdexcept>

std::vector<std::uint64_t> generate_catalan_sequence(std::size_t n) {
    std::vector<std::uint64_t> c(n + 1, 0);
    c[0] = 1;

    for (std::size_t i = 1; i <= n; ++i) {
        for (std::size_t j = 0; j < i; ++j) {
            c[i] += c[j] * c[i - 1 - j];
        }
    }
    return c;
}
