#include <iostream>
#include <vector>
#include <cmath>
#include <numbers>
#include <span>
#include <algorithm>
#include <numeric>
#include <iomanip>

namespace vieta_solver {

/* Клас для представлення алгебраїчного многочлена довільного степеня */
class Polynomial {
public:
    explicit Polynomial(std::span<const double> roots) {
        coeffs_.resize(roots.size() + 1, 0.0);
        coeffs_[0] = 1.0;

        for (size_t i = 0; i < roots.size(); ++i) {
            const double r = roots[i];
            for (size_t j = i + 1; j > 0; --j) {
                coeffs_[j] = coeffs_[j] - r * coeffs_[j - 1];
            }
        }
    }

    [[nodiscard]] std::span<const double> coefficients() const noexcept {
        return coeffs_;
    }

    [[nodiscard]] size_t degree() const noexcept {
        return coeffs_.empty() ? 0 : coeffs_.size() - 1;
    }

private:
    std::vector<double> coeffs_;
};

/* Клас для розв'язання симетричних систем через теорему Вієта */
class SymmetricSystemSolver {
public:
    /* Перетворення степеневих сум s_k на елементарні многочлени e_k за формулами Ньютона */
    [[nodiscard]] static std::vector<double> compute_elementary_polynomials(std::span<const double> power_sums) {
        const size_t n = power_sums.size();
        std::vector<double> e(n + 1, 0.0);
        e[0] = 1.0;

        for (size_t k = 1; k <= n; ++k) {
            double sum = 0.0;
            double sign = 1.0;

            for (size_t j = 1; j < k; ++j) {
                sum += sign * e[k - j] * power_sums[j - 1];
                sign = -sign;
            }

            sum += sign * power_sums[k - 1];
            e[k] = sum / static_cast<double>(k);
        }

        return e;
    }

    /* Розв'язання кубічного рівняння t^3 - e1*t^2 + e2*t - e3 = 0 тригонометричним методом Вієта */
    [[nodiscard]] static std::vector<double> solve_cubic(double e1, double e2, double e3) {
        const double shift = e1 / 3.0;
        const double p = e2 - (e1 * e1) / 3.0;
        const double q = -e3 + (e1 * e2) / 3.0 - (2.0 * e1 * e1 * e1) / 27.0;

        const double disc = (q * q) / 4.0 + (p * p * p) / 27.0;

        std::vector<double> roots;
        roots.reserve(3);

        if (disc <= 1e-12) {
            const double r = std::sqrt(- (p * p * p) / 27.0);
            const double phi = std::acos(std::clamp(-q / (2.0 * r), -1.0, 1.0));
            const double factor = 2.0 * std::cbrt(r);

            roots.push_back(factor * std::cos(phi / 3.0) + shift);
            roots.push_back(factor * std::cos((phi + 2.0 * std::numbers::pi) / 3.0) + shift);
            roots.push_back(factor * std::cos((phi + 4.0 * std::numbers::pi) / 3.0) + shift);
        } else {
            const double u = std::cbrt(-q / 2.0 + std::sqrt(disc));
            const double v = std::cbrt(-q / 2.0 - std::sqrt(disc));
            roots.push_back(u + v + shift);
        }

        std::ranges::sort(roots);
        return roots;
    }
};

} // namespace vieta_solver

int main() {
    using namespace vieta_solver;

    // Демонстрація 1: Синтез многочлена за заданими коренями
    const std::vector<double> known_roots = {1.0, 2.0, 3.0};
    const Polynomial poly(known_roots);

    std::cout << std::fixed << std::setprecision(4);
    std::cout << "Синтезований многочлен за коренями {1, 2, 3}:\n";
    std::cout << "P(x) = x^3 + (" << poly.coefficients()[1] << ")x^2 + ("
              << poly.coefficients()[2] << ")x + (" << poly.coefficients()[3] << ")\n\n";

    // Демонстрація 2: Розв'язання симетричної системи:
    // x + y + z = 6
    // x^2 + y^2 + z^2 = 14
    // x^3 + y^3 + z^3 = 36
    const std::vector<double> power_sums = {6.0, 14.0, 36.0};
    const auto e = SymmetricSystemSolver::compute_elementary_polynomials(power_sums);

    std::cout << "Обчислені коефіцієнти Вієта за сумами степенів:\n";
    std::cout << "e1 = " << e[1] << ", e2 = " << e[2] << ", e3 = " << e[3] << "\n\n";

    auto roots = SymmetricSystemSolver::solve_cubic(e[1], e[2], e[3]);

    std::cout << "Усі розв'язки системи (перестановки вектора коренів):\n";
    size_t perm_idx = 1;
    do {
        std::cout << "Розв'язок #" << perm_idx++ << ": (x = " << roots[0]
                  << ", y = " << roots[1] << ", z = " << roots[2] << ")\n";
    } while (std::ranges::next_permutation(roots).found);

    return 0;
}
