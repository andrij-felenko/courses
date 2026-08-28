#include <vector>
#include <span>
#include <algorithm>
#include <cmath>
#include <iostream>

class Polynomial {
public:
    std::vector<double> coeffs;

    explicit Polynomial(size_t degree = 0) : coeffs(degree + 1, 0.0) {}
    explicit Polynomial(std::vector<double> c) : coeffs(std::move(c)) {
        normalize();
    }

    [[nodiscard]] size_t degree() const noexcept {
        return coeffs.empty() ? 0 : coeffs.size() - 1;
    }

    // Інваріант нормалізації: видалення фіктивних нульових старших коефіцієнтів
    void normalize() noexcept {
        while (coeffs.size() > 1 && std::abs(coeffs.back()) < 1e-12) {
            coeffs.pop_back();
        }
        if (coeffs.empty()) {
            coeffs.push_back(0.0);
        }
    }

    [[nodiscard]] friend Polynomial operator+(const Polynomial& a, const Polynomial& b) {
        const size_t max_deg = std::max(a.degree(), b.degree());
        Polynomial res(max_deg);
        for (size_t i = 0; i <= max_deg; ++i) {
            const double val_a = (i <= a.degree()) ? a.coeffs[i] : 0.0;
            const double val_b = (i <= b.degree()) ? b.coeffs[i] : 0.0;
            res.coeffs[i] = val_a + val_b;
        }
        res.normalize();
        return res;
    }

    [[nodiscard]] friend Polynomial operator*(const Polynomial& a, const Polynomial& b) {
        if (a.coeffs.empty() || b.coeffs.empty()) {
            return Polynomial(0);
        }
        Polynomial res(a.degree() + b.degree());
        for (size_t i = 0; i <= a.degree(); ++i) {
            for (size_t j = 0; j <= b.degree(); ++j) {
                res.coeffs[i + j] += a.coeffs[i] * b.coeffs[j];
            }
        }
        res.normalize();
        return res;
    }
};
