#include <iostream>
#include <vector>
#include <cstdint>
#include <optional>
#include <span >
#include <concepts>

namespace wieferich {

using uint128_t = unsigned __int128;

// Ідіоматична обгортка швидкого піднесення до степеня за модулем p²
[[nodiscard]] constexpr std::uint64_t power_mod(std::uint64_t base, std::uint64_t exp, uint128_t mod_val) noexcept {
    uint128_t res = 1;
    uint128_t b = base % mod_val;

    while (exp > 0) {
        if (exp & 1) {
            res = (res * b) % mod_val;
        }
        b = (b * b) % mod_val;
        exp >>= 1;
    }
    return static_cast<std::uint64_t>(res);
}

// Предикат верифікації простого числа Віферіха
[[nodiscard]] bool is_wieferich(std::uint64_t prime) noexcept {
    if (prime <= 3) {
        return false;
    }

    const uint128_t prime_sq = static_cast<uint128_t>(prime) * prime;
    const std::uint64_t rem = power_mod(2, prime - 1, prime_sq);

    return rem == 1;
}

// Генерація простих чисел через решето Ератосфена (RAII через std::vector)
[[nodiscard]] std::vector<std::uint64_t> generate_primes(std::uint64_t limit) {
    std::vector<bool> is_prime(limit + 1, true);
    is_prime[0] = is_prime[1] = false;

    for (std::uint64_t p = 2; p * p <= limit; ++p) {
        if (is_prime[p]) {
            for (std::uint64_t i = p * p; i <= limit; i += p) {
                is_prime[i] = false;
            }
        }
    }

    std::vector<std::uint64_t> primes;
    for (std::uint64_t p = 2; p <= limit; ++p) {
        if (is_prime[p]) {
            primes.push_back(p);
        }
    }
    return primes;
}

// Пошук у заданому числовому діапазоні
[[nodiscard]] std::vector<std::uint64_t> find_wieferich_primes(std::uint64_t limit) {
    const auto primes = generate_primes(limit);
    std::vector<std::uint64_t> wieferich_found;

    for (const auto p : primes) {
        if (is_wieferich(p)) {
            wieferich_found.push_back(p);
        }
    }
    return wieferich_found;
}

} // namespace wieferich

int main() {
    std::cout << "Пошук простих чисел Віферіха (C++20)...\n";

    const auto found = wieferich::find_wieferich_primes(10000);
    std::cout << "Знайдено у діапазоні до 10000: " << found.size() << '\n';
    for (const auto p : found) {
        std::cout << "  -> p = " << p << '\n';
    }

    std::cout << "\nВерифікація контрольних значень:\n";
    std::cout << "  1093: " << (wieferich::is_wieferich(1093) ? "Так (Віферіх)" : "Ні") << '\n';
    std::cout << "  3511: " << (wieferich::is_wieferich(3511) ? "Так (Віферіх)" : "Ні") << '\n';
    std::cout << "  7919: " << (wieferich::is_wieferich(7919) ? "Так (Віферіх)" : "Ні") << '\n';

    return 0;
}
