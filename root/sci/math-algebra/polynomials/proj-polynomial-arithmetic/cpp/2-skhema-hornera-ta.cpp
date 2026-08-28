#include <iostream>
#include <span>
#include <vector>

// Обчислення P(x) за схемою Горнера для довільного неперервного діапазону коефіцієнтів.
// coeffs: послідовність коефіцієнтів [a0, a1, ..., an], де coeffs[i] відповідає моному a_i * x^i.
// Забезпечує noexcept таconstexpr сумісність.
[[nodiscard]] constexpr double evaluate_horner(std::span<const double> coeffs, double x) noexcept {
    if (coeffs.empty()) {
        return 0.0;
    }
    double result = coeffs.back();
    for (auto it = coeffs.rbegin() + 1; it != coeffs.rend(); ++it) {
        result = result * x + *it;
    }
    return result;
}
