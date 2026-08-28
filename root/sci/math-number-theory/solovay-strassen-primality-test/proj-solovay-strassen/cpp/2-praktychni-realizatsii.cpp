#include <iostream>
#include <random>
#include <numeric>
#include <cstdint>
#include <vector>
#include <utility>
#include <iomanip>

namespace number_theory {

enum class PrimalityStatus {
    Composite,
    ProbablyPrime
};

class SolovayStrassenTester {
public:
    // Конструктор ініціалізує 64-бітний генератор Вихру Мерсенна
    explicit SolovayStrassenTester(std::uint64_t seed = std::random_device{}())
        : rng_(seed) {}

    // Модульне множення без переповнення
    [[nodiscard]] static constexpr std::uint64_t mul_mod(std::uint64_t a, std::uint64_t b, std::uint64_t mod) noexcept {
        return static_cast<std::uint64_t>((static_cast<unsigned __int128>(a) * b) % mod);
    }

    // Модульне піднесення до степеня O(log exp)
    [[nodiscard]] static constexpr std::uint64_t power_mod(std::uint64_t base, std::uint64_t exp, std::uint64_t mod) noexcept {
        std::uint64_t result = 1;
        base %= mod;
        while (exp > 0) {
            if (exp & 1) {
                result = mul_mod(result, base, mod);
            }
            base = mul_mod(base, base, mod);
            exp >>= 1;
        }
        return result;
    }

    // Обчислення символу Якобі (a / n)
    [[nodiscard]] static constexpr int jacobi_symbol(std::int64_t a, std::int64_t n) noexcept {
        if (n <= 0 || n % 2 == 0) {
            return 0;
        }

        a = (a % n + n) % n;
        int result = 1;

        while (a != 0) {
            while (a % 2 == 0) {
                a /= 2;
                const std::int64_t n_mod8 = n % 8;
                if (n_mod8 == 3 || n_mod8 == 5) {
                    result = -result;
                }
            }

            std::swap(a, n);

            if (a % 4 == 3 && n % 4 == 3) {
                result = -result;
            }

            a %= n;
        }

        return (n == 1) ? result : 0;
    }

    // Виконання розширеного тесту Соловея–Штрассена
    [[nodiscard]] PrimalityStatus is_prime(std::uint64_t n, std::size_t rounds = 30) {
        if (n < 2) return PrimalityStatus::Composite;
        if (n == 2 || n == 3) return PrimalityStatus::ProbablyPrime;
        if (n % 2 == 0) return PrimalityStatus::Composite;

        // Рівномірний розподіл у діапазоні [2, n - 1] без bias
        std::uniform_int_distribution<std::uint64_t> dist(2, n - 1);

        for (std::size_t i = 0; i < rounds; ++i) {
            const std::uint64_t a = dist(rng_);

            // Рання перевірка спільного дільника
            if (std::gcd(a, n) > 1) {
                return PrimalityStatus::Composite;
            }

            const std::uint64_t x = power_mod(a, (n - 1) / 2, n);
            const int jac = jacobi_symbol(static_cast<std::int64_t>(a), static_cast<std::int64_t>(n));
            const std::uint64_t jac_mod = static_cast<std::uint64_t>((jac % static_cast<std::int64_t>(n) + n) % n);

            // Перевірка критерію Ейлера
            if (x != jac_mod) {
                return PrimalityStatus::Composite; // Знайдено свідка складеності
            }
        }

        return PrimalityStatus::ProbablyPrime;
    }

private:
    std::mt19937_64 rng_;
};

} // namespace number_theory

int main() {
    number_theory::SolovayStrassenTester tester;

    const std::vector<std::uint64_t> test_cases = {
        561, 1105, 1729, 2821, 6601, 8911, 10007, 10009, 104729, 65537
    };

    std::cout << "=== Демонстрація тесту Соловея–Штрассена (C++23) ===\n";
    for (const auto n : test_cases) {
        const auto status = tester.is_prime(n, 30);
        std::cout << "Число " << std::setw(8) << n << " : "
                  << (status == number_theory::PrimalityStatus::ProbablyPrime 
                      ? "ЙМОВІРНО ПРОСТЕ" : "СКЛАДЕНЕ")
                  << '\n';
    }

    return 0;
}
