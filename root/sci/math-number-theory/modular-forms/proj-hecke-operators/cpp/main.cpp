#include <iostream>
#include <vector>
#include <cmath>
#include <cstdint>
#include <iomanip>
#include <string>
#include <span>
#include <algorithm>
#include <stdexcept>

namespace ModularEngine {

class ModularFormSeries {
private:
    std::size_t max_degree_;
    std::size_t weight_;
    std::vector<std::int64_t> coeffs_;

public:
    explicit ModularFormSeries(std::size_t max_degree, std::size_t weight = 0)
        : max_degree_(max_degree), weight_(weight), coeffs_(max_degree + 1, 0) {}

    [[nodiscard]] std::size_t degree() const noexcept { return max_degree_; }
    [[nodiscard]] std::size_t weight() const noexcept { return weight_; }
    [[nodiscard]] std::span<const std::int64_t> coefficients() const noexcept { return coeffs_; }
    
    std::int64_t& operator[](std::size_t idx) { 
        if (idx > max_degree_) {
            throw std::out_of_range("Індекс степеня q виходить за межі урізаного ряду");
        }
        return coeffs_[idx]; 
    }

    std::int64_t operator[](std::size_t idx) const { 
        if (idx > max_degree_) {
            throw std::out_of_range("Індекс степеня q виходить за межі урізаного ряду");
        }
        return coeffs_[idx]; 
    }

    /* Обчислення арифметичної функції sigma_k(n) = sum_{d | n} d^k */
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

    /* Фабричні методи побудови рядів Ейзенштейна */
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

    static ModularFormSeries create_e8(std::size_t max_deg) {
        ModularFormSeries e8(max_deg, 8);
        e8[0] = 1;
        for (std::size_t n = 1; n <= max_deg; ++n) {
            e8[n] = 480 * static_cast<std::int64_t>(sigma(static_cast<std::uint32_t>(n), 7));
        }
        return e8;
    }

    static ModularFormSeries create_e10(std::size_t max_deg) {
        ModularFormSeries e10(max_deg, 10);
        e10[0] = 1;
        for (std::size_t n = 1; n <= max_deg; ++n) {
            e10[n] = -264 * static_cast<std::int64_t>(sigma(static_cast<std::uint32_t>(n), 9));
        }
        return e10;
    }

    static ModularFormSeries create_e14(std::size_t max_deg) {
        ModularFormSeries e14(max_deg, 14);
        e14[0] = 1;
        for (std::size_t n = 1; n <= max_deg; ++n) {
            e14[n] = -24 * static_cast<std::int64_t>(sigma(static_cast<std::uint32_t>(n), 13));
        }
        return e14;
    }

    /* Генерація параболічного дискримінанта Delta ваги 12 */
    static ModularFormSeries create_delta(std::size_t max_deg) {
        auto e4 = create_e4(max_deg);
        auto e6 = create_e6(max_deg);
        auto e4_3 = e4 * e4 * e4;
        auto e6_2 = e6 * e6;

        ModularFormSeries delta(max_deg, 12);
        for (std::size_t n = 0; n <= max_deg; ++n) {
            delta[n] = (e4_3[n] - e6_2[n]) / 1728;
        }
        return delta;
    }

    /* Алгебраїчні операції над урізаними рядами */
    ModularFormSeries operator+(const ModularFormSeries& rhs) const {
        std::size_t deg = std::min(max_degree_, rhs.max_degree_);
        ModularFormSeries res(deg, weight_);
        for (std::size_t n = 0; n <= deg; ++n) {
            res[n] = coeffs_[n] + rhs.coeffs_[n];
        }
        return res;
    }

    ModularFormSeries operator-(const ModularFormSeries& rhs) const {
        std::size_t deg = std::min(max_degree_, rhs.max_degree_);
        ModularFormSeries res(deg, weight_);
        for (std::size_t n = 0; n <= deg; ++n) {
            res[n] = coeffs_[n] - rhs.coeffs_[n];
        }
        return res;
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

    bool operator==(const ModularFormSeries& rhs) const {
        std::size_t deg = std::min(max_degree_, rhs.max_degree_);
        for (std::size_t n = 0; n <= deg; ++n) {
            if (coeffs_[n] != rhs.coeffs_[n]) {
                return false;
            }
        }
        return true;
    }

    /* Дія оператора Гекке T_p */
    [[nodiscard]] ModularFormSeries hecke_operator(std::uint32_t p) const {
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
    auto e8 = ModularFormSeries::create_e8(MAX_N);
    auto e10 = ModularFormSeries::create_e10(MAX_N);
    auto e14 = ModularFormSeries::create_e14(MAX_N);

    // 1. Перевірка алгебраїчної структури кільця M_*(SL(2, Z))
    std::cout << "=== Перевірка алгебраїчних тотожностей у просторах M_k ===\n";
    auto e4_2 = e4 * e4;
    auto e4_e6 = e4 * e6;
    auto e4_2_e6 = e4_2 * e6;

    std::cout << "  1. E8 == E4^2:            " << (e8 == e4_2 ? "ПІДТВЕРДЖЕНО" : "ПОМИЛКА") << "\n";
    std::cout << "  2. E10 == E4 * E6:        " << (e10 == e4_e6 ? "ПІДТВЕРДЖЕНО" : "ПОМИЛКА") << "\n";
    std::cout << "  3. E14 == E4^2 * E6:      " << (e14 == e4_2_e6 ? "ПІДТВЕРДЖЕНО" : "ПОМИЛКА") << "\n\n";

    // 2. Обчислення параболічного дискримінанта Delta (вага 12)
    auto delta = ModularFormSeries::create_delta(MAX_N);

    std::cout << "=== Коефіцієнти Фур'є E4, E6 та Delta (функція Рамануджана tau(n)) ===\n";
    std::cout << std::setw(4) << "n" << std::setw(14) << "E4(n)" 
              << std::setw(14) << "E6(n)" << std::setw(18) << "Delta(n) [tau(n)]\n";
    std::cout << std::string(52, '-') << "\n";

    for (std::size_t n = 1; n <= MAX_N; ++n) {
        std::cout << std::setw(4) << n << std::setw(14) << e4[n] 
                  << std::setw(14) << e6[n] << std::setw(18) << delta[n] << "\n";
    }

    // 3. Застосування операторів Гекке T_2 та T_3 до власної форми Delta
    auto t2_delta = delta.hecke_operator(2);
    auto t3_delta = delta.hecke_operator(3);

    std::cout << "\n=== Перевірка дії оператора Гекке T_2 (tau(2) = " << delta[2] << ") ===\n";
    std::cout << std::setw(4) << "n" << std::setw(14) << "tau(n)" 
              << std::setw(18) << "T_2(Delta)[n]" << std::setw(20) << "tau(2)*tau(n)\n";
    std::cout << std::string(58, '-') << "\n";

    for (std::size_t n = 1; n <= 5; ++n) {
        std::int64_t expected = delta[2] * delta[n];
        std::cout << std::setw(4) << n << std::setw(14) << delta[n] 
                  << std::setw(18) << t2_delta[n] << std::setw(20) << expected 
                  << " (" << (t2_delta[n] == expected ? "ЗБІГАЄТЬСЯ" : "ПОМИЛКА") << ")\n";
    }

    std::cout << "\n=== Перевірка дії оператора Гекке T_3 (tau(3) = " << delta[3] << ") ===\n";
    std::cout << std::setw(4) << "n" << std::setw(14) << "tau(n)" 
              << std::setw(18) << "T_3(Delta)[n]" << std::setw(20) << "tau(3)*tau(n)\n";
    std::cout << std::string(58, '-') << "\n";

    for (std::size_t n = 1; n <= 3; ++n) {
        std::int64_t expected = delta[3] * delta[n];
        std::cout << std::setw(4) << n << std::setw(14) << delta[n] 
                  << std::setw(18) << t3_delta[n] << std::setw(20) << expected 
                  << " (" << (t3_delta[n] == expected ? "ЗБІГАЄТЬСЯ" : "ПОМИЛКА") << ")\n";
    }

    // 4. Перевірка мультиплікативних тотожностей Рамануджана
    std::cout << "\n=== Перевірка мультиплікативних властивостей функції Рамануджана ===\n";
    std::int64_t tau6 = delta[6];
    std::int64_t tau2_tau3 = delta[2] * delta[3];
    std::cout << "  tau(6) = " << tau6 << ", tau(2)*tau(3) = " << tau2_tau3 
              << " ==> " << (tau6 == tau2_tau3 ? "МУЛЬТИПЛІКАТИВНІСТЬ ПІДТВЕРДЖЕНО" : "ПОМИЛКА") << "\n";

    std::int64_t tau10 = delta[10];
    std::int64_t tau2_tau5 = delta[2] * delta[5];
    std::cout << "  tau(10) = " << tau10 << ", tau(2)*tau(5) = " << tau2_tau5 
              << " ==> " << (tau10 == tau2_tau5 ? "МУЛЬТИПЛІКАТИВНІСТЬ ПІДТВЕРДЖЕНО" : "ПОМИЛКА") << "\n";

    std::int64_t tau4_expected = delta[2] * delta[2] - 2048 * delta[1];
    std::cout << "  tau(4) = " << delta[4] << ", tau(2)^2 - 2^11*tau(1) = " << tau4_expected 
              << " ==> " << (delta[4] == tau4_expected ? "СТЕПЕНЕВА ТОТОЖНІСТЬ ПІДТВЕРДЖЕНА" : "ПОМИЛКА") << "\n";

    // 5. Перевірка межі Деліня для простих p
    std::cout << "\n=== Перевірка гіпотези Рамануджана (межа Деліня: |tau(p)| <= 2*p^(11/2)) ===\n";
    const std::vector<std::uint32_t> primes = {2, 3, 5, 7};
    for (auto p : primes) {
        double bound = 2.0 * std::pow(static_cast<double>(p), 5.5);
        std::int64_t val = delta[p];
        std::cout << "  p = " << p << ": |tau(" << p << ")| = " << std::abs(val) 
                  << ", 2*p^(11/2) = " << std::fixed << std::setprecision(2) << bound 
                  << " ==> " << (static_cast<double>(std::abs(val)) <= bound ? "МЕЖА ДЕЛІНЯ ВИКОНУЄТЬСЯ" : "ПОРУШЕННЯ") << "\n";
    }

    return 0;
}
