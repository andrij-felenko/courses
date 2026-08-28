#include <vector>
#include <cstddef>
#include <concepts>
#include <span>

namespace math {

struct MatrixDim {
    std::size_t rows;
    std::size_t cols;
};

/*
 * Кронекерів добуток для плоских динамічних векторів з кеш-оптимізованим проходом.
 */
[[nodiscard]] inline std::vector<double> kronecker_product(
    std::span<const double> A, MatrixDim dimA,
    std::span<const double> B, MatrixDim dimB
) {
    MatrixDim dimC{dimA.rows * dimB.rows, dimA.cols * dimB.cols};
    std::vector<double> C(dimC.rows * dimC.cols, 0.0);

    for (std::size_t ia = 0; ia < dimA.rows; ++ia) {
        for (std::size_t ja = 0; ja < dimA.cols; ++ja) {
            const double a_val = A[ia * dimA.cols + ja];
            for (std::size_t ib = 0; ib < dimB.rows; ++ib) {
                const std::size_t row_c = ia * dimB.rows + ib;
                for (std::size_t jb = 0; jb < dimB.cols; ++jb) {
                    const std::size_t col_c = ja * dimB.cols + jb;
                    C[row_c * dimC.cols + col_c] = a_val * B[ib * dimB.cols + jb];
                }
            }
        }
    }
    return C;
}

} // namespace math
