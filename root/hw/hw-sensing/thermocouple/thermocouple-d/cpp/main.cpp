#include <array>
#include <span>
#include <concepts>

namespace sensing {

/* Коефіцієнти оберненого полінома NIST Type K для діапазону 0..500 °C */
inline constexpr std::array<double, 10> k_inv_poly_0_500 = {
    0.000000E+00,  2.508355E+01,  7.860106E-02,
   -2.503131E-01,  8.315270E-02, -1.228034E-02,
    9.804036E-04, -4.413030E-05,  1.057734E-06,
   -1.052755E-08
};

/* Обчислення полінома за схемою Горнера з перевіркою типів під час компіляції */
template <std::floating_point T>
[[nodiscard]] constexpr T evaluate_nist_horner(std::span<const T> coeffs, T x) noexcept {
    T result = coeffs.back();
    for (auto it = coeffs.rbegin() + 1; it != coeffs.rend(); ++it) {
        result = result * x + *it;
    }
    return result;
}

[[nodiscard]] constexpr double evaluate_type_k_0_to_500(double mv_total) noexcept {
    return evaluate_nist_horner(std::span{k_inv_poly_0_500}, mv_total);
}

} // namespace sensing
