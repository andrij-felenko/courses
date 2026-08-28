#include <iostream>
#include <cstdint>
#include <utility>
#include <vector>
#include <bit>

namespace math {

/*
 * Обчислює пару (Lₙ, Lₙ₊₁) за час O(log n) в ідіоматичному стилі C++20
 * Повертає std::pair<std::uint64_t, std::uint64_t>
 */
constexpr std::pair<std::uint64_t, std::uint64_t> fast_lucas_pair(std::uint32_t n) noexcept {
    if (n == 0) {
        return {2ULL, 1ULL};
    }

    const int bit_length = 32 - std::countl_zero(n);
    std::uint64_t a = 2ULL; // L₀
    std::uint64_t b = 1ULL; // L₁
    std::uint32_t k = 0;

    for (int i = bit_length - 1; i >= 0; --i) {
        const std::int64_t sign = (k % 2 == 0) ? 1 : -1;
        const std::uint64_t next_a = a * a - static_cast<std::uint64_t>(2 * sign);
        const std::uint64_t next_b = a * b - static_cast<std::uint64_t>(sign);

        a = next_a;
        b = next_b;
        k *= 2;

        if ((n >> i) & 1U) {
            const std::uint64_t temp = a + b;
            a = b;
            b = temp;
            k += 1;
        }
    }

    return {a, b};
}

constexpr std::uint64_t fast_lucas(std::uint32_t n) noexcept {
    return fast_lucas_pair(n).first;
}

/*
 * Тест простоти Люка-Лемера для M_p = 2^p - 1 у C++20
 */
bool lucas_lehmer_test(std::uint32_t p) noexcept {
    if (p == 2) return true;
    const std::uint64_t m_p = (1ULL << p) - 1ULL;
    std::uint64_t s = 4ULL;
    for (std::uint32_t i = 0; i < p - 2; ++i) {
        s = (s * s - 2ULL) % m_p;
    }
    return s == 0ULL;
}

} // namespace math

int main() {
    std::cout << "Обчислення чисел Люка (C++20):\n";
    for (std::uint32_t n = 0; n <= 15; ++n) {
        std::cout << "L_" << n << " = " << math::fast_lucas(n) << '\n';
    }

    std::cout << "\nПеревірка чисел Мерсенна M_p:\n";
    const std::vector<std::uint32_t> primes = {3, 5, 7, 13, 17, 19, 31};
    for (auto p : primes) {
        std::cout << "M_" << p << " є " << (math::lucas_lehmer_test(p) ? "ПРОСТИМ" : "СКЛАДЕНИМ") << '\n';
    }
    return 0;
}
