#include <iostream>
#include <vector>
#include <complex>
#include <numbers>
#include <cstdint>
#include <stdexcept>
#include <span>

class EisensteinSeriesCalculator {
public:
    // Поодиноке обчислення суми дільників sigma_k(n) = sum_{d|n} d^k
    static constexpr std::uint64_t compute_sigma_single(std::uint32_t n, std::uint32_t k) noexcept {
        std::uint64_t sum = 0;
        for (std::uint32_t d = 1; d * d <= n; ++d) {
            if (n % d == 0) {
                std::uint64_t term1 = 1;
                for (std::uint32_t p = 0; p < k; ++p) term1 *= d;
                sum += term1;

                std::uint32_t d2 = n / d;
                if (d2 != d) {
                    std::uint64_t term2 = 1;
                    for (std::uint32_t p = 0; p < k; ++p) term2 *= d2;
                    sum += term2;
                }
            }
        }
        return sum;
    }

    // Решето для масового табулювання сум дільників sigma_k(1...max_n)
    static std::vector<std::uint64_t> compute_sigma_sieve(std::size_t max_n, std::uint32_t k) {
        std::vector<std::uint64_t> sigma(max_n + 1, 0);
        for (std::size_t d = 1; d <= max_n; ++d) {
            std::uint64_t d_pow = 1;
            for (std::uint32_t p = 0; p < k; ++p) d_pow *= d;

            for (std::size_t mult = d; mult <= max_n; mult += d) {
                sigma[mult] += d_pow;
            }
        }
        return sigma;
    }

    struct EisensteinCoefficients {
        std::vector<std::int64_t> e4;
        std::vector<std::int64_t> e6;
    };

    // Генерація q-розкладу для E4 та E6 через решето
    static EisensteinCoefficients generate_e4_e6(std::size_t max_n) {
        const auto s3 = compute_sigma_sieve(max_n, 3);
        const auto s5 = compute_sigma_sieve(max_n, 5);

        EisensteinCoefficients res;
        res.e4.resize(max_n + 1, 0);
        res.e6.resize(max_n + 1, 0);

        res.e4[0] = 1;
        res.e6[0] = 1;

        for (std::size_t n = 1; n <= max_n; ++n) {
            res.e4[n] = static_cast<std::int64_t>(240 * s3[n]);
            res.e6[n] = -static_cast<std::int64_t>(504 * s5[n]);
        }

        return res;
    }

    // Розрахунок функції Рамануджана tau(n) через Delta = (E4^3 - E6^2) / 1728
    static std::vector<std::int64_t> generate_ramanujan_tau(std::size_t max_n,
                                                             std::span<const std::int64_t> e4,
                                                             std::span<const std::int64_t> e6) {
        std::vector<std::int64_t> e4_sq(max_n + 1, 0);
        std::vector<std::int64_t> e4_cube(max_n + 1, 0);
        std::vector<std::int64_t> e6_sq(max_n + 1, 0);
        std::vector<std::int64_t> tau(max_n + 1, 0);

        for (std::size_t i = 0; i <= max_n; ++i) {
            for (std::size_t j = 0; j <= max_n - i; ++j) {
                e4_sq[i + j] += e4[i] * e4[j];
            }
        }

        for (std::size_t i = 0; i <= max_n; ++i) {
            for (std::size_t j = 0; j <= max_n - i; ++j) {
                e4_cube[i + j] += e4_sq[i] * e4[j];
            }
        }

        for (std::size_t i = 0; i <= max_n; ++i) {
            for (std::size_t j = 0; j <= max_n - i; ++j) {
                e6_sq[i + j] += e6[i] * e6[j];
            }
        }

        for (std::size_t n = 0; n <= max_n; ++n) {
            const auto diff = e4_cube[n] - e6_sq[n];
            tau[n] = diff / 1728;
        }

        return tau;
    }

    // Оцінка значення E4(tau)
    static std::complex<double> eval_e4(std::complex<double> tau, std::size_t terms = 50) {
        if (tau.imag() <= 0.0) {
            throw std::invalid_argument("Параметр tau має лежати строго у Верхній півплощині (Im(tau) > 0)");
        }

        using namespace std::complex_literals;
        const auto pi = std::numbers::pi;
        const std::complex<double> q = std::exp(2.0 * pi * 1i * tau);

        std::complex<double> sum = 1.0;
        std::complex<double> q_pow = q;

        for (std::size_t n = 1; n <= terms; ++n) {
            const auto s3 = compute_sigma_single(static_cast<std::uint32_t>(n), 3);
            sum += static_cast<double>(240 * s3) * q_pow;
            q_pow *= q;

            if (std::abs(q_pow) < 1e-15) {
                break;
            }
        }

        return sum;
    }
};

int main() {
    try {
        constexpr std::size_t N = 10;
        const auto [e4, e6] = EisensteinSeriesCalculator::generate_e4_e6(N);
        const auto tau = EisensteinSeriesCalculator::generate_ramanujan_tau(N, e4, e6);

        std::cout << "--- Коефіцієнти q-розкладу рядів Ейзенштейна та функції Рамануджана (C++) ---\n";
        std::cout << "n  | E4(n)        | E6(n)        | Tau(n) (Рамануджан)\n";
        std::cout << "---|--------------|--------------|--------------------\n";
        for (std::size_t n = 0; n <= N; ++n) {
            std::cout << n << "  | " << e4[n] << "          | " << e6[n] << "          | " << tau[n] << "\n";
        }

        const std::complex<double> tau_val{0.0, 1.0};
        const auto val_e4 = EisensteinSeriesCalculator::eval_e4(tau_val);

        std::cout << "\nЗначення E4(i) = " << val_e4.real() << " + " << val_e4.imag() << "i\n";
    } catch (const std::exception& ex) {
        std::cerr << "Помилка: " << ex.what() << '\n';
        return 1;
    }

    return 0;
}
