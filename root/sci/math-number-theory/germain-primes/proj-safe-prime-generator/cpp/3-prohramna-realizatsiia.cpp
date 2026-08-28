#include <iostream>
#include <vector>
#include <optional>
#include <random>
#include <cstdint>

namespace crypto {

struct SafePrimePair {
    std::uint64_t germain_p;
    std::uint64_t safe_q;
};

class SafePrimeGenerator {
private:
    static constexpr std::uint64_t SMALL_PRIMES[] = {
        3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97
    };

    static std::uint64_t mod_pow(std::uint64_t base, std::uint64_t exp, std::uint64_t mod) noexcept {
        std::uint64_t result = 1;
        base %= mod;
        while (exp > 0) {
            if (exp & 1) {
                result = static_cast<std::uint64_t>(static_cast<unsigned __int128>(result) * base % mod);
            }
            base = static_cast<std::uint64_t>(static_cast<unsigned __int128>(base) * base % mod);
            exp >>= 1;
        }
        return result;
    }

    static bool passes_sieve(std::uint64_t n) noexcept {
        for (auto p : SMALL_PRIMES) {
            if (n == p) return true;
            if (n % p == 0) return false;
        }
        return true;
    }

public:
    static bool is_prime_miller_rabin(std::uint64_t n, std::size_size rounds = 25) {
        if (n < 2) return false;
        if (n == 2 || n == 3) return true;
        if (n % 2 == 0) return false;

        std::uint64_t d = n - 1;
        std::size_t s = 0;
        while ((d & 1) == 0) {
            d >>= 1;
            s++;
        }

        std::mt19937_64 rng(std::random_device{}());
        std::uniform_int_distribution<std::uint64_t> dist(2, n - 2);

        for (std::size_t i = 0; i < rounds; ++i) {
            std::uint64_t a = dist(rng);
            std::uint64_t x = mod_pow(a, d, n);

            if (x == 1 || x == n - 1) continue;

            bool composite = true;
            for (std::size_t r = 1; r < s; ++r) {
                x = static_cast<std::uint64_t>(static_cast<unsigned __int128>(x) * x % n);
                if (x == n - 1) {
                    composite = false;
                    break;
                }
            }
            if (composite) return false;
        }
        return true;
    }

    static std::optional<SafePrimePair> generate(std::uint64_t min_p, std::uint64_t max_p) {
        for (std::uint64_t p = min_p; p <= max_p; ++p) {
            /* Затискання: перевіряємо лише варіанти p = 6k + 5 */
            if (p % 6 != 5) continue;

            std::uint64_t q = 2 * p + 1;

            if (!passes_sieve(p) || !passes_sieve(q)) continue;

            if (is_prime_miller_rabin(p) && is_prime_miller_rabin(q)) {
                return SafePrimePair{p, q};
            }
        }
        return std::nullopt;
    }
};

} // namespace crypto

int main() {
    std::cout << "=== Генератор безпечних простих чисел (C++20) ===\n";
    auto result = crypto::SafePrimeGenerator::generate(1000000, 2000000);
    if (result) {
        std::cout << "Знайдено просте Софі Жермен p = " << result->germain_p << "\n";
        std::cout << "Знайдено безпечне просте q = 2p + 1 = " << result->safe_q << "\n";
    } else {
        std::cout << "У даному діапазоні безпечних простих чисел не знайдено.\n";
    }
    return 0;
}
