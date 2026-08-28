#include <vector>
#include <span>
#include <cmath>
#include <expected>

enum class MatrixError { NotPositiveDefinite, InvalidSize };

/* Факторизація Холецького симетричної додатно визначеної матриці розміру N x N */
[[nodiscard]] std::expected<std::vector<double>, MatrixError> cholesky_factorize(
    std::span<const double> a,
    size_t n
) {
    if (a.size() != n * n || n == 0) {
        return std::unexpected(MatrixError::InvalidSize);
    }

    std::vector<double> l(n * n, 0.0);

    for (size_t j = 0; j < n; ++j) {
        double sum_sq = 0.0;
        for (size_t k = 0; k < j; ++k) {
            sum_sq += l[j * n + k] * l[j * n + k];
        }

        double diag = a[j * n + j] - sum_sq;
        if (diag <= 1e-15) {
            return std::unexpected(MatrixError::NotPositiveDefinite);
        }

        double l_jj = std::sqrt(diag);
        l[j * n + j] = l_jj;
        double inv_l_jj = 1.0 / l_jj;

        for (size_t i = j + 1; i < n; ++i) {
            double sum_prod = 0.0;
            for (size_t k = 0; k < j; ++k) {
                sum_prod += l[i * n + k] * l[j * n + k];
            }
            l[i * n + j] = (a[i * n + j] - sum_prod) * inv_l_jj;
        }
    }

    return l;
}
