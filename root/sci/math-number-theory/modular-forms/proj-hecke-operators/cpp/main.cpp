#include <iostream>
#include <vector>
#include <cmath>
#include <cstdint>
#include <iomanip>

namespace ModularEngine {

class ModularFormSeries {
private:
    std::size_t max_degree_;
    std::size_t weight_;
    std::vector<std::int64_t> coeffs_;

public:
    explicit ModularFormSeries(std::size_t max_degree, std::size_t weight = 0)
        : max_degree_(max_degree), weight_(weight), coeffs_(max_degree + 1, 0) {}

    std::size_t degree() const noexcept { return max_degree_; }
    std::size_t weight() const noexcept { return weight_; }
    
    std::int64_t& operator[](std::size_t idx) { return coeffs_.at(idx); }
    std::int64_t operator[](std::size_t idx) const { return coeffs_.at(idx); }

    static std::uint64_t sigma(std::uint32_t n, std::uint32_t k) {
        std::uint64_t sum = 0;
        for (std::uint32_t d = 1; d * d <= n; ++d) {
            if (n % d == 0) {
                sum += static_cast<std::uint64_t>(std::pow(d, k));
                std::uint32_t div2 = n / d;
                if (div2 != d) {
                    sum += static_cast<std::uint64_t>(std::pow(div2, k));
                }
            }
        }
        return sum;
    }

    static ModularFormSeries create_e4(std::size_t max_deg) {
        ModularFormSeries e4(max_deg, 4);
        e4[0] = 1;
        for (std::size_t n = 1; n <= max_deg; ++n) {
            e4[n] = 240 * static_cast<std::int64_t>(sigma(static_cast<std::uint32_t>(n), 3));
        }
        return e4;
    }

    static ModularFormSeries create_e6(std::size_t max_deg) {
        ModularFormSeries e6(max_deg, 6);
        e6[0] = 1;
        for (std::size_t n = 1; n <= max_deg; ++n) {
            e6[n] = -504 * static_cast<std::int64_t>(sigma(static_cast<std::uint32_t>(n), 5));
        }
        return e6;
    }

    ModularFormSeries operator*(const ModularFormSeries& rhs) const {
        std::size_t deg = std::min(max_degree_, rhs.max_degree_);
        ModularFormSeries res(deg, weight_ + rhs.weight_);
        for (std::size_t n = 0; n <= deg; ++n) {
            std::int64_t sum = 0;
            for (std::size_t k = 0; k <= n; ++k) {
                sum += coeffs_[k] * rhs.coeffs_[n - k];
            }
            res[n] = sum;
        }
        return res;
    }

    ModularFormSeries hecke_operator(std::uint32_t p) const {
        ModularFormSeries result(max_degree_, weight_);
        std::uint64_t p_pow = static_cast<std::uint64_t>(std::pow(p, weight_ - 1));

        for (std::size_t n = 0; n <= max_degree_; ++n) {
            std::int64_t term1 = (n * p <= max_degree_) ? coeffs_[n * p] : 0;
            std::int64_t term2 = (n % p == 0) ? static_cast<std::int64_t>(p_pow) * coeffs_[n / p] : 0;
            result[n] = term1 + term2;
        }
        return result;
    }
};

} // namespace ModularEngine

int main() {
    constexpr std::size_t MAX_N = 10;
    using namespace ModularEngine;

    auto e4 = ModularFormSeries::create_e4(MAX_N);
    auto e6 = ModularFormSeries::create_e6(MAX_N);

    auto e4_3 = e4 * e4 * e4;
    auto e6_2 = e6 * e6;

    ModularFormSeries delta(MAX_N, 12);
    for (std::size_t n = 0; n <= MAX_N; ++n) {
        delta[n] = (e4_3[n] - e6_2[n]) / 1728;
    }

    std::cout << "=== Коефіцієнти Фур'є E4, E6 та Delta (tau(n)) ===\n";
    std::cout << std::setw(4) << "n" << std::setw(14) << "E4(n)" 
              << std::setw(14) << "E6(n)" << std::setw(18) << "Delta(n) [tau(n)]\n";
    std::cout << std::string(50, '-') << "\n";

    for (std::size_t n = 1; n <= MAX_N; ++n) {
        std::cout << std::setw(4) << n << std::setw(14) << e4[n] 
                  << std::setw(14) << e6[n] << std::setw(18) << delta[n] << "\n";
    }

    // Застосування оператора Гекке T_2 до параболічної форми Delta
    auto t2_delta = delta.hecke_operator(2);

    std::cout << "\n=== Перевірка теореми Гекке: T_2(Delta) = tau(2) * Delta ===\n";
    std::cout << "Коефіцієнт tau(2) = " << delta[2] << "\n";
    std::cout << std::setw(4) << "n" << std::setw(14) << "tau(n)" 
              << std::setw(18) << "T_2(Delta)[n]" << std::setw(20) << "tau(2)*tau(n)\n";
    std::cout << std::string(56, '-') << "\n";

    for (std::size_t n = 1; n <= 5; ++n) {
        std::int64_t expected = delta[2] * delta[n];
        std::cout << std::setw(4) << n << std::setw(14) << delta[n] 
                  << std::setw(18) << t2_delta[n] << std::setw(20) << expected 
                  << " (" << (t2_delta[n] == expected ? "ЗБІГАЄТЬСЯ" : "ПОМИЛКА") << ")\n";
    }

    return 0;
}
