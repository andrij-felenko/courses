#include <cstddef>
#include <concepts>
#include <span>
#include <vector>
#include <utility>

namespace math {

/*
 * Тип з нульовим розміром: віртуальна одинична матриця.
 * Не займає жодного байта у пам'яті (sizeof == 1 за стандартом C++).
 */
template <std::size_t N>
struct IdentityMatrix {
    static constexpr std::size_t size = N;

    [[nodiscard]] constexpr double operator()(std::size_t i, std::size_t j) const noexcept {
        return (i == j) ? 1.0 : 0.0;
    }
};

template <std::size_t Rows, std::size_t Cols>
class DenseMatrix {
    std::array<double, Rows * Cols> data_{};
public:
    constexpr DenseMatrix() noexcept = default;

    [[nodiscard]] constexpr double& operator()(std::size_t r, std::size_t c) noexcept {
        return data_[r * Cols + c];
    }

    [[nodiscard]] constexpr double operator()(std::size_t r, std::size_t c) const noexcept {
        return data_[r * Cols + c];
    }
};

/*
 * Перевантаження оператора множення для віртуальної одиничної матриці.
 * Складність O(1) за часом і пам'яттю: повертає вихідну матрицю без обчислень.
 */
template <std::size_t Rows, std::size_t Cols>
[[nodiscard]] constexpr const DenseMatrix<Rows, Cols>& operator*(
    const DenseMatrix<Rows, Cols>& A,
    [[maybe_unused]] const IdentityMatrix<Cols>& I
) noexcept {
    return A; // A * I = A
}

} // namespace math
