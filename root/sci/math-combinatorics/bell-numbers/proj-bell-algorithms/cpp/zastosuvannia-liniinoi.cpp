#include <iostream>
#include <vector>
#include <cstdint>

// Обчислення B_n mod p за допомогою рекурентності Тушара
std::uint64_t bell_mod_p(std::uint64_t n, std::uint64_t p) {
    if (p <= 1) return 0;
    if (n <= 1) return 1 % p;

    // Крок 1. Обчислюємо B_0 ... B_p mod p
    std::vector<std::uint64_t> b(p + 1, 0);
    std::vector<std::uint64_t> row(p + 1, 0);

    row[0] = 1;
    b[0] = 1 % p;

    for (std::size_t i = 1; i <= p; ++i) {
        std::uint64_t prev = row[i - 1];
        row[0] = prev;
        for (std::size_t j = 1; j <= i; ++j) {
            std::uint64_t temp = row[j];
            row[j] = (row[j - 1] + prev) % p;
            prev = temp;
        }
        b[i] = row[i];
    }

    if (n <= p) return b[n];

    // Крок 2. Кільцевий буфер за порівнянням Тушара
    const std::size_t cap = p + 1;
    for (std::uint64_t k = 1; k <= n - p; ++k) {
        b[(k + p) % cap] = (b[(k + 1) % cap] + b[k % cap]) % p;
    }

    return b[n % cap];
}

int main() {
    std::uint64_t n = 100;
    std::uint64_t p = 7;
    std::cout << "B_" << n << " mod " << p << " = " << bell_mod_p(n, p) << "\n";
    return 0;
}
