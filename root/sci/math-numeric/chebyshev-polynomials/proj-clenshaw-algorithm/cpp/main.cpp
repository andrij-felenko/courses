#include <iostream>
#include <vector>
#include <cmath>
#include <numbers>
#include <iomanip>
#include <span>

// Обчислення значення рядка Чебишова за допомогою алгоритму Кленшоу
constexpr double clenshaw_eval(std::span<const double> coeffs, double x) noexcept {
    if (coeffs.empty()) return 0.0;
    if (coeffs.size() == 1) return coeffs[0] * 0.5;

    double b_k1 = 0.0; // b_{k+1}
    double b_k2 = 0.0; // b_{k+2}

    for (std::size_t k = coeffs.size() - 1; k >= 1; --k) {
        double b_k = 2.0 * x * b_k1 - b_k2 + coeffs[k];
        b_k2 = b_k1;
        b_k1 = b_k;
    }

    return x * b_k1 - b_k2 + 0.5 * coeffs[0];
}

// Побудова коефіцієнтів інтерполяційного полінома Чебишова
template <typename Func>
std::vector<double> fit_chebyshev_series(Func&& func, std::size_t n) {
    std::vector<double> nodes(n);
    std::vector<double> f_vals(n);

    for (std::size_t k = 0; k < n; ++k) {
        nodes[k] = std::cos((2.0 * static_cast<double>(k + 1) - 1.0) * std::numbers::pi / (2.0 * static_cast<double>(n)));
        f_vals[k] = func(nodes[k]);
    }

    std::vector<double> coeffs(n);
    for (std::size_t m = 0; m < n; ++m) {
        double sum = 0.0;
        for (std::size_t k = 0; k < n; ++k) {
            double t_mk = std::cos(static_cast<double>(m) * (2.0 * static_cast<double>(k) + 1.0) * std::numbers::pi / (2.0 * static_cast<double>(n)));
            sum += f_vals[k] * t_mk;
        }
        coeffs[m] = (2.0 / static_cast<double>(n)) * sum;
    }

    return coeffs;
}

int main() {
    auto runge_function = [](double x) noexcept {
        return 1.0 / (1.0 + 25.0 * x * x);
    };

    constexpr std::size_t N = 11;
    const std::vector<double> coeffs = fit_chebyshev_series(runge_function, N);

    const std::vector<double> test_points = {-0.95, -0.5, 0.0, 0.5, 0.95};

    std::cout << std::setw(8) << "x" << " | "
              << std::setw(15) << "Exact" << " | "
              << std::setw(15) << "Approx" << " | "
              << std::setw(12) << "Error" << "\n";
    std::cout << "----------------------------------------------------------\n";

    for (double pt : test_points) {
        double exact = runge_function(pt);
        double approx = clenshaw_eval(coeffs, pt);
        double err = std::abs(exact - approx);

        std::cout << std::fixed << std::setprecision(2) << std::setw(8) << pt << " | "
                  << std::setprecision(8) << std::setw(15) << exact << " | "
                  << std::setw(15) << approx << " | "
                  << std::scientific << std::setprecision(4) << std::setw(12) << err << "\n";
    }

    return 0;
}
