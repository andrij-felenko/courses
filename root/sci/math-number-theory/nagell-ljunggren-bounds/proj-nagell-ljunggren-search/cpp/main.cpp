#include <iostream>
#include <vector>
#include <optional>
#include <cmath>
#include <cstdint>
#include <span>
#include <array>

namespace NagellLjunggren {

class SolverEngine {
private:
    static constexpr std::array<std::uint64_t, 10> sieve_primes = {
        3, 5, 7, 11, 13, 17, 19, 23, 29, 31
    };

    static std::uint64_t power_mod(std::uint64_t base, std::uint64_t exp, std::uint64_t mod) noexcept {
        std::uint64_t result = 1;
        base %= mod;
        while (exp > 0) {
            if (exp & 1) {
                result = static_cast<unsigned __int128>(result) * base % mod;
            }
            base = static_cast<unsigned __int128>(base) * base % mod;
            exp >>= 1;
        }
        return result;
    }

    static std::uint64_t repunit_mod(std::uint64_t x, std::uint64_t n, std::uint64_t p) noexcept {
        const std::uint64_t x_mod = x % p;
        if (x_mod == 1) {
            return n % p;
        }
        const std::uint64_t num = (power_mod(x_mod, n, p) + p - 1) % p;
        const std::uint64_t den = x_mod - 1;
        const std::uint64_t den_inv = power_mod(den, p - 2, p);
        return static_cast<unsigned __int128>(num) * den_inv % p;
    }

    static bool is_qth_residue(std::uint64_t val, std::uint64_t q, std::uint64_t p) noexcept {
        if (val % p == 0) return true;
        std::uint64_t a = p - 1, b = q;
        while (b != 0) {
            std::uint64_t t = b;
            b = a % b;
            a = t;
        }
        const std::uint64_t gcd_q = a;
        const std::uint64_t exp = (p - 1) / gcd_q;
        return power_mod(val, exp, p) == 1;
    }

public:
    struct Solution {
        std::uint64_t x;
        std::uint64_t n;
        std::uint64_t y;
        std::uint64_t q;
    };

    static bool passes_modular_sieve(std::uint64_t x, std::uint64_t n, std::uint64_t q) noexcept {
        for (const std::uint64_t p : sieve_primes) {
            if (q % (p - 1) == 0) continue;
            const std::uint64_t rep_mod = repunit_mod(x, n, p);
            if (!is_qth_residue(rep_mod, q, p)) {
                return false;
            }
        }
        return true;
    }

    static std::optional<Solution> verify_candidate(std::uint64_t x, std::uint64_t n, std::uint64_t q) noexcept {
        if (!passes_modular_sieve(x, n, q)) {
            return std::nullopt;
        }

        unsigned __int128 repunit = 0;
        unsigned __int128 current_term = 1;
        for (std::uint64_t i = 0; i < n; ++i) {
            repunit += current_term;
            if (i + 1 < n) {
                current_term *= x;
                if (current_term > UINT64_MAX) return std::nullopt;
            }
        }

        const double double_rep = static_cast<double>(repunit);
        const double y_double = std::pow(double_rep, 1.0 / static_cast<double>(q));
        const std::uint64_t y_candidate = static_cast<std::uint64_t>(std::round(y_double));

        if (y_candidate < 2) return std::nullopt;

        unsigned __int128 pow_y = 1;
        for (std::uint64_t i = 0; i < q; ++i) {
            pow_y *= y_candidate;
            if (pow_y > repunit) break;
        }

        if (pow_y == repunit) {
            return Solution{x, n, y_candidate, q};
        }
        return std::nullopt;
    }
};

} // namespace NagellLjunggren

int main() {
    std::cout << "Пошуковий двигун Нагеля-Люнггрена (C++20)...\n";

    std::vector<NagellLjunggren::SolverEngine::Solution> solutions;

    for (std::uint64_t x = 2; x <= 100; ++x) {
        for (std::uint64_t n = 3; n <= 30; ++n) {
            for (std::uint64_t q = 2; q <= 10; ++q) {
                if (auto sol = NagellLjunggren::SolverEngine::verify_candidate(x, n, q)) {
                    solutions.push_back(*sol);
                    std::cout << "ЗНАЙДЕНО РОЗВ'ЯЗОК: x = " << sol->x
                              << ", n = " << sol->n
                              << ", y = " << sol->y
                              << ", q = " << sol->q << "\n";
                }
            }
        }
    }

    std::cout << "Усього знайдено розв'язків: " << solutions.size() << "\n";
    return 0;
}
