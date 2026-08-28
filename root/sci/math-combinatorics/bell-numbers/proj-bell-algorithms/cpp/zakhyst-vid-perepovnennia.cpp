#include <iostream>
#include <vector>
#include <cstdint>
#include <stdexcept>

// Генерація перших n + 1 чисел Белла B_0 ... B_n
std::vector<std::uint64_t> compute_bell_numbers(std::size_t n) {
    if (n > 25) {
        throw std::overflow_error("Значення n > 25 викликає переповнення std::uint64_t");
    }

    std::vector<std::uint64_t> bell(n + 1);
    std::vector<std::uint64_t> row(n + 1);

    row[0] = 1;
    bell[0] = 1;

    for (std::size_t i = 1; i <= n; ++i) {
        std::uint64_t prev = row[0];
        row[0] = row[i - 1];
        bell[i] = row[0];

        for (std::size_t j = 1; j <= i; ++j) {
            std::uint64_t temp = row[j];
            row[j] = row[j - 1] + prev;
            prev = temp;
        }
    }

    return bell;
}

int main() {
    try {
        constexpr std::size_t N = 15;
        const auto bell = compute_bell_numbers(N);

        std::cout << "Перші 16 чисел Белла:\n";
        for (std::size_t i = 0; i <= N; ++i) {
            std::cout << "B_" << i << " = " << bell[i] << "\n";
        }
    } catch (const std::exception& e) {
        std::cerr << "Помилка: " << e.what() << "\n";
        return 1;
    }
    return 0;
}
