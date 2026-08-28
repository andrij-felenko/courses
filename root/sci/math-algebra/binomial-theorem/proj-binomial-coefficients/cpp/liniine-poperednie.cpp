#include <cstdint>
#include <vector>
#include <stdexcept>

// Стандартний клас RAII в C++20 для безпечного збереження модулярних масивів
class ModularCombinatorics {
public:
    static constexpr std::uint64_t MOD = 1'000'000'007ULL;

    explicit ModularCombinatorics(std::size_t max_n)
        : fact_(max_n + 1, 1), inv_fact_(max_n + 1, 1) {
        
        for (std::size_t i = 1; i <= max_n; ++i) {
            fact_[i] = (fact_[i - 1] * i) % MOD;
        }

        inv_fact_[max_n] = power_mod(fact_[max_n], MOD - 2);
        for (std::size_t i = max_n; i > 0; --i) {
            inv_fact_[i - 1] = (inv_fact_[i] * i) % MOD;
        }
    }

    [[nodiscard]] std::uint64_t ncr(std::size_t n, std::size_t k) const noexcept {
        if (k > n || n >= fact_.size()) return 0;
        return (fact_[n] * inv_fact_[k] % MOD) * inv_fact_[n - k] % MOD;
    }

private:
    std::vector<std::uint64_t> fact_;
    std::vector<std::uint64_t> inv_fact_;

    static std::uint64_t power_mod(std::uint64_t base, std::uint64_t exp) noexcept {
        std::uint64_t res = 1;
        base %= MOD;
        while (exp > 0) {
            if (exp & 1) res = (res * base) % MOD;
            base = (base * base) % MOD;
            exp >>= 1;
        }
        return res;
    }
};
