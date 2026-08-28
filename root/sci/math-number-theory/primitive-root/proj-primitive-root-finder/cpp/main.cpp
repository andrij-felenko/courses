#include <iostream>
#include <vector>
#include <optional>
#include <cstdint>
#include <numeric>

namespace number_theory {

// Сучасний обчислювач модульного піднесення до степеня
constexpr std::uint64_t power_mod(std::uint64_t base, std::uint64_t exp, std::uint64_t mod) noexcept {
    std::uint64_t result = 1;
    base %= mod;
    while (exp > 0) {
        if (exp & 1) {
            result = static_cast<std::uint64_t>(
                (static_cast<unsigned __int128>(result) * base) % mod);
        }
        base = static_cast<std::uint64_t>(
            (static_cast<unsigned __int128>(base) * base) % mod);
        exp >>= 1;
    }
    return result;
}

// Обчислення функції Ейлера φ(n)
std::uint64_t euler_phi(std::uint64_t n) {
    std::uint64_t result = n;
    for (std::uint64_t p = 2; p * p <= n; ++p) {
        if (n % p == 0) {
            while (n % p == 0) {
                n /= p;
            }
            result -= result / p;
        }
    }
    if (n > 1) {
        result -= result / n;
    }
    return result;
}

// Знаходження унікальних простих множників n
std::vector<std::uint64_t> get_prime_factors(std::uint64_t n) {
    std::vector<std::uint64_t> factors;
    for (std::uint64_t p = 2; p * p <= n; ++p) {
        if (n % p == 0) {
            factors.push_back(p);
            while (n % p == 0) {
                n /= p;
            }
        }
    }
    if (n > 1) {
        factors.push_back(n);
    }
    return factors;
}

// Перевірка існування первісного кореня (Критерій Ґаусса)
bool has_primitive_root(std::uint64_t n) noexcept {
    if (n == 2 || n == 4) return true;
    if (n % 2 == 0) n /= 2;
    if (n % 2 == 0) return false;

    for (std::uint64_t p = 3; p * p <= n; p += 2) {
        if (n % p == 0) {
            while (n % p == 0) n /= p;
            return (n == 1);
        }
    }
    return true;
}

// Знаходження найменшого первісного кореня
std::optional<std::uint64_t> find_primitive_root(std::uint64_t n) {
    if (!has_primitive_root(n)) {
        return std::nullopt;
    }
    if (n == 2) return 1;

    const std::uint64_t phi = euler_phi(n);
    const auto factors = get_prime_factors(phi);

    for (std::uint64_t g = 2; g < n; ++g) {
        if (std::gcd(g, n) != 1) continue;

        bool is_primitive = true;
        for (const std::uint64_t q : factors) {
            if (power_mod(g, phi / q, n) == 1) {
                is_primitive = false;
                break;
            }
        }
        if (is_primitive) {
            return g;
        }
    }
    return std::nullopt;
}

} // namespace number_theory

int main() {
    const std::vector<std::uint64_t> test_moduli = {7, 9, 14, 15, 17, 25, 31, 81};

    for (const auto n : test_moduli) {
        if (auto root = number_theory::find_primitive_root(n)) {
            std::cout << "Модуль " << n << ": найменший первісний корінь = " << *root << '\n';
        } else {
            std::cout << "Модуль " << n << ": первісного кореня НЕ ІСНУЄ\n";
        }
    }
    return 0;
}
