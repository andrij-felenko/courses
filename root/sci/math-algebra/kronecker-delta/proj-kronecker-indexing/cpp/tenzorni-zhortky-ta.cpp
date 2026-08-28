#include <array>
#include <span>
#include <cstddef>

namespace math {

template <std::size_t N>
using Vector = std::array<double, N>;

template <std::size_t N>
using Matrix = std::array<std::array<double, N>, N>;

template <std::size_t N>
using Tensor3D = std::array<std::array<std::array<double, N>, N>, N>;

/*
 * Високопродуктивна згортка з використанням std::span та constexpr розмірів.
 * Символ Кронекера delta_jl виключає зайвий вимір j під час компіляції.
 */
template <std::size_t Dim = 3>
[[nodiscard]] constexpr Matrix<Dim> contract_tensor_delta(
    const Tensor3D<Dim>& A,
    const Vector<Dim>& v
) noexcept {
    Matrix<Dim> result{};
    for (std::size_t i = 0; i < Dim; ++i) {
        for (std::size_t l = 0; l < Dim; ++l) {
            double sum = 0.0;
            for (std::size_t k = 0; k < Dim; ++k) {
                sum += A[i][l][k] * v[k];
            }
            result[i][l] = sum;
        }
    }
    return result;
}

/*
 * Векторний добуток з нульовими накладними витратами.
 */
[[nodiscard]] constexpr Vector<3> cross_product(
    const Vector<3>& a,
    const Vector<3>& b
) noexcept {
    return {
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0]
    };
}

} // namespace math
