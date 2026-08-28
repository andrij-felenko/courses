#include <iostream>
#include <vector>
#include <span>
#include <concepts>
#include <utility>

// Обчислення значення многочлена у точці x0 з використанням std::span
template <std::floating_point T>
T horner_eval(std::span<const T> coeffs, T x0) {
    if (coeffs.empty()) return T{0};
    
    T result = coeffs.front(); // a[n]
    for (size_t i = 1; i < coeffs.size(); ++i) {
        result = result * x0 + coeffs[i];
    }
    return result;
}

// Синтетичне ділення P(x) на (x - x0)
// Повертає пару {вектор коефіцієнтів частки Q(x), остача R}
template <std::floating_point T>
std::pair<std::vector<T>, T> horner_synthetic_div(std::span<const T> coeffs, T x0) {
    if (coeffs.size() <= 1) {
        return {{}, coeffs.empty() ? T{0} : coeffs.front()};
    }

    const size_t n = coeffs.size() - 1;
    std::vector<T> q(n);
    q[0] = coeffs[0]; // b[n-1] = a[n]

    for (size_t i = 1; i < n; ++i) {
        q[i] = coeffs[i] + x0 * q[i - 1];
    }

    T remainder = coeffs.back() + x0 * q.back();
    return {q, remainder};
}

int main() {
    // P(x) = 2x³ - 6x² + 2x - 1, коефіцієнти від старшого до молодшого
    std::vector<double> coeffs = {2.0, -6.0, 2.0, -1.0};
    double x0 = 3.0;

    double val = horner_eval<double>(coeffs, x0);
    std::cout << "P(" << x0 << ") = " << val << "\n";

    auto [q, rem] = horner_synthetic_div<double>(coeffs, x0);
    std::cout << "Остача R = " << rem << "\n";
    std::cout << "Частка Q(x): ";
    for (double c : q) std::cout << c << " ";
    std::cout << "\n";

    return 0;
}
