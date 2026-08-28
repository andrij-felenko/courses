// cpp
#include <iostream>
#include <cstdint>
#include <random>
#include <optional>
#include <concepts>

namespace bpp {

class MillerRabinTester {
public:
    explicit MillerRabinTester(std::uint64_t seed = std::random_device{}())
        : rng_(seed) {}

    // Повертає true, якщо n просте з імовірністю помилки <= (1/4)^k
    [[nodiscard]] bool is_prime(std::uint64_t n, int k = 20) {
        if (n < 2) return false;
        if (n == 2 || n == 3) return true;
        if (n % 2 == 0) return false;

        // Розклад n - 1 = 2^s * d
        std::uint64_t d = n - 1;
        int s = 0;
        while ((d & 1) == 0) {
            d >>= 1;
            s++;
        }

        std::uniform_int_distribution<std::uint64_t> dist(2, n - 2);

        for (int i = 0; i < k; ++i) {
            const std::uint64_t a = dist(rng_);
            if (!single_test(n, a, d, s)) {
                return false; // Засвідчено складеність
            }
        }
        return true;
    }

private:
    std::mt19937_64 rng_;

    [[nodiscard]] static constexpr std::uint64_t mul_mod(std::uint64_t a, std::uint64_t b, std::uint64_t mod) noexcept {
#if defined(__SIZEOF_INT128__)
        return static_cast<std::uint64_t>((static_cast<unsigned __int128>(a) * b) % mod);
#else
        std::uint64_t res = 0;
        a %= mod;
        while (b > 0) {
            if (b & 1) res = (res + a) % mod;
            a = (a * 2) % mod;
            b >>= 1;
        }
        return res;
#endif
    }

    [[nodiscard]] static constexpr std::uint64_t power_mod(std::uint64_t base, std::uint64_t exp, std::uint64_t mod) noexcept {
        std::uint64_t res = 1;
        base %= mod;
        while (exp > 0) {
            if (exp & 1) res = mul_mod(res, base, mod);
            base = mul_mod(base, base, mod);
            exp >>= 1;
        }
        return res;
    }

    [[nodiscard]] static bool single_test(std::uint64_t n, std::uint64_t a, std::uint64_t d, int s) noexcept {
        std::uint64_t x = power_mod(a, d, n);
        if (x == 1 || x == n - 1) return true;

        for (int r = 1; r < s; ++r) {
            x = mul_mod(x, x, n);
            if (x == n - 1) return true;
            if (x == 1) return false; // Нетривіальний корінь з 1 -> складене
        }
        return false;
    }
};

} // namespace bpp

int main() {
    bpp::MillerRabinTester tester;
    constexpr std::uint64_t candidate = 1000000007ULL;
    constexpr int rounds = 20;

    if (tester.is_prime(candidate, rounds)) {
        std::cout << "Число " << candidate << " є простим із високою ймовірністю.\n";
    } else {
        std::cout << "Число " << candidate << " є складеним.\n";
    }
}
