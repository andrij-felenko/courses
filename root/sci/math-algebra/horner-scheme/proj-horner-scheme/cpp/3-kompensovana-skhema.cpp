#include <iostream>
#include <vector>
#include <span>
#include <cmath>
#include <iomanip>

// Компенсована схема Горнера для типів з підтримкою std::fma
template <typename T>
T compensated_horner(std::span<const T> coeffs, T x0) {
    if (coeffs.empty()) return T{0};

    T s = coeffs.front(); // a[n]
    T c = T{0};

    for (size_t i = 1; i < coeffs.size(); ++i) {
        // TwoProduct через fma
        T p = s * x0;
        T pi = std::fma(s, x0, -p);

        // TwoSum (Knuth)
        T s_new = p + coeffs[i];
        T b_virt = s_new - p;
        T a_virt = s_new - b_virt;
        T b_err = coeffs[i] - b_virt;
        T a_err = p - a_virt;
        T sigma = a_err + b_err;

        s = s_new;
        c = std::fma(c, x0, pi + sigma);
    }

    return s + c;
}

int main() {
    // P(x) = (x - 1)⁶ = x⁶ - 6x⁵ + 15x⁴ - 20x³ + 15x² - 6x + 1
    std::vector<double> coeffs = {1.0, -6.0, 15.0, -20.0, 15.0, -6.0, 1.0};
    double x0 = 1.000001;

    double comp_res = compensated_horner<double>(coeffs, x0);
    double exact_res = std::pow(x0 - 1.0, 6.0);

    std::cout << std::setprecision(16);
    std::cout << "Компенсований Горнер: " << comp_res << "\n";
    std::cout << "Точне (x - 1)⁶:        " << exact_res << "\n";

    return 0;
}
