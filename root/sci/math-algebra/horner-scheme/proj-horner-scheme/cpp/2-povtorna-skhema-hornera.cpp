#include <iostream>
#include <vector>
#include <span>
#include <concepts>

// Обчислює коефіцієнти розкладу Тейлора: derivs[k] = P^(k)(x0) / k!
template <std::floating_point T>
std::vector<T> horner_taylor_coefficients(std::span<const T> coeffs, T x0) {
    if (coeffs.empty()) return {};

    std::vector<T> work(coeffs.begin(), coeffs.end());
    const size_t n = coeffs.size() - 1;
    std::vector<T> derivs(n + 1);

    for (size_t k = 0; k <= n; ++k) {
        for (size_t i = 0; i < n - k; ++i) {
            work[i + 1] += x0 * work[i];
        }
        derivs[k] = work[n - k];
    }

    return derivs;
}

int main() {
    // P(x) = x³ - 3x² + 3x - 1 = (x - 1)³
    std::vector<double> coeffs = {1.0, -3.0, 3.0, -1.0}; // від a3 до a0
    double x0 = 2.0;

    auto derivs = horner_taylor_coefficients<double>(coeffs, x0);

    std::cout << "Коефіцієнти Тейлора навколо x0 = " << x0 << ":\n";
    for (size_t k = 0; k < derivs.size(); ++k) {
        std::cout << "P^(" << k << ")(" << x0 << ") / " << k << "! = " << derivs[k] << "\n";
    }

    return 0;
}
