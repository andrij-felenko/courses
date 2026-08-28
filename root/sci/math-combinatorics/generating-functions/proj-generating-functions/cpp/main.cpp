#include <iostream>
#include <vector>
#include <cmath>
#include <stdexcept>
#include <iomanip>

/**
 * @brief Клас формального степенного ряду (Formal Power Series) мовою C++.
 * Реалізує обчислення коефіцієнтів ряду за модулем x^N (з усіченням до N).
 */
class FormalPowerSeries {
private:
    std::size_t degree_;
    std::vector<double> coeffs_;

public:
    explicit FormalPowerSeries(const std::vector<double>& coeffs, std::size_t degree = 16)
        : degree_(degree), coeffs_(degree, 0.0) {
        std::size_t limit = std::min(coeffs.size(), degree_);
        for (std::size_t i = 0; i < limit; ++i) {
            coeffs_[i] = coeffs[i];
        }
    }

    [[nodiscard]] std::size_t degree() const noexcept { return degree_; }
    [[nodiscard]] const std::vector<double>& coeffs() const noexcept { return coeffs_; }
    [[nodiscard]] double operator[](std::size_t idx) const { return coeffs_.at(idx); }

    FormalPowerSeries operator+(const FormalPowerSeries& other) const {
        std::vector<double> res(degree_, 0.0);
        for (std::size_t i = 0; i < degree_; ++i) {
            res[i] = coeffs_[i] + other.coeffs_[i];
        }
        return FormalPowerSeries(res, degree_);
    }

    FormalPowerSeries operator-(const FormalPowerSeries& other) const {
        std::vector<double> res(degree_, 0.0);
        for (std::size_t i = 0; i < degree_; ++i) {
            res[i] = coeffs_[i] - other.coeffs_[i];
        }
        return FormalPowerSeries(res, degree_);
    }

    /// Дискретна згортка коефіцієнтів O(N^2)
    FormalPowerSeries operator*(const FormalPowerSeries& other) const {
        std::vector<double> res(degree_, 0.0);
        for (std::size_t i = 0; i < degree_; ++i) {
            for (std::size_t j = 0; j < degree_ - i; ++j) {
                res[i + j] += coeffs_[i] * other.coeffs_[j];
            }
        }
        return FormalPowerSeries(res, degree_);
    }

    /// Обчислення оберненого ряду 1 / A(x)
    FormalPowerSeries invert() const {
        if (std::abs(coeffs_[0]) < 1e-12) {
            throw std::invalid_argument("Вільний член A[0] дорівнює 0, обернений ряд не існує.");
        }

        std::vector<double> b(degree_, 0.0);
        b[0] = 1.0 / coeffs_[0];

        for (std::size_t k = 1; k < degree_; ++k) {
            double acc = 0.0;
            for (std::size_t i = 1; i <= k; ++i) {
                acc += coeffs_[i] * b[k - i];
            }
            b[k] = -acc / coeffs_[0];
        }

        return FormalPowerSeries(b, degree_);
    }
};

int main() {
    constexpr std::size_t N = 12;

    // Обчислення Фібоначчі: F(x) = x / (1 - x - x^2)
    FormalPowerSeries Q({1.0, -1.0, -1.0}, N);
    FormalPowerSeries P({0.0, 1.0}, N);
    
    FormalPowerSeries Q_inv = Q.invert();
    FormalPowerSeries F = P * Q_inv;

    std::cout << "Числа Фібоначчі через твірну функцію C++:\n";
    for (std::size_t i = 0; i < 10; ++i) {
        std::cout << "F[" << i << "] = " << std::llround(F[i]) << "\n";
    }

    // Обчислення чисел Каталана через ітерацію C = 1 + x*C^2
    FormalPowerSeries C({1.0}, 8);
    FormalPowerSeries one({1.0}, 8);

    for (std::size_t iter = 0; iter < 8; ++iter) {
        FormalPowerSeries C_sq = C * C;
        std::vector<double> x_C_sq_coeffs(8, 0.0);
        for (std::size_t i = 0; i < 7; ++i) {
            x_C_sq_coeffs[i + 1] = C_sq[i];
        }
        FormalPowerSeries x_C_sq(x_C_sq_coeffs, 8);
        C = one + x_C_sq;
    }

    std::cout << "\nЧисла Каталана через твірну функцію C++:\n";
    for (std::size_t i = 0; i < 8; ++i) {
        std::cout << "C[" << i << "] = " << std::llround(C[i]) << "\n";
    }

    return 0;
}
