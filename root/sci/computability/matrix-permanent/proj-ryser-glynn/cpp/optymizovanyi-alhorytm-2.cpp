#include <vector>
#include <span>
#include <cstddef>
#include <cstdint>
#include <bit>
#include <cmath>

namespace math {

// Ідіоматичний C++20 алгоритм Ґлінна для подвійної точності
[[nodiscard]] double permanent_glynn(std::span<const double> matrix, std::size_t n) {
    if (n == 0 || matrix.size() < n * n) {
        return 0.0;
    }

    std::vector<double> delta(n, 1.0);
    std::vector<double> row_sum(n, 0.0);

    for (std::size_t i = 0; i < n; ++i) {
        for (std::size_t j = 0; j < n; ++j) {
            row_sum[i] += matrix[i * n + j];
        }
    }

    double total_sum = 0.0;
    const std::uint64_t num_subsets = 1ULL << (n - 1);
    std::uint64_t prev_gray = 0;

    for (std::uint64_t i = 0; i < num_subsets; ++i) {
        const std::uint64_t gray = i ^ (i >> 1);

        if (i > 0) {
            const std::uint64_t diff = gray ^ prev_gray;
            const std::size_t bit_idx = static_cast<std::size_t>(std::countr_zero(diff)) + 1;

            delta[bit_idx] = -delta[bit_idx];
            const double factor = 2.0 * delta[bit_idx];

            for (std::size_t r = 0; r < n; ++r) {
                row_sum[r] += factor * matrix[r * n + bit_idx];
            }
        }

        double prod = 1.0;
        for (std::size_t r = 0; r < n; ++r) {
            prod *= row_sum[r];
        }

        double delta_prod = 1.0;
        for (std::size_t j = 0; j < n; ++j) {
            delta_prod *= delta[j];
        }

        total_sum += delta_prod * prod;
        prev_gray = gray;
    }

    return total_sum / static_cast<double>(1ULL << (n - 1));
}

} // namespace math
