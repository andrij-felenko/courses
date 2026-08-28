// Модулярне обчислення числа Каталана мовою C++ з узагальненим типом
#include <cstdint>

class ModularCatalan {
public:
    static std::uint64_t compute(std::uint32_t n, std::uint64_t mod) {
        std::uint64_t res = 1;
        for (std::uint32_t i = 1; i <= n; ++i) {
            std::uint64_t num = (4ULL * i - 2) % mod;
            std::uint64_t den_inv = mod_inverse(i + 1, mod);
            res = (res * num) % mod;
            res = (res * den_inv) % mod;
        }
        return res;
    }

private:
    static std::uint64_t power(std::uint64_t base, std::uint64_t exp, std::uint64_t mod) noexcept {
        std::uint64_t res = 1;
        base %= mod;
        while (exp > 0) {
            if (exp & 1) res = (res * base) % mod;
            base = (base * base) % mod;
            exp >>= 1;
        }
        return res;
    }

    static std::uint64_t mod_inverse(std::uint64_t val, std::uint64_t mod) noexcept {
        return power(val, mod - 2, mod);
    }
};
