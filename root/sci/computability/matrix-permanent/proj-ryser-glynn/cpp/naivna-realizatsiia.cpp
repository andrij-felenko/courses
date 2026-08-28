#include <vector>
#include <numeric>
#include <algorithm>
#include <span>
#include <cstddef>

namespace math {

// Ідіоматичний C++20 наївний алгоритм обчислення перманента
[[nodiscard]] double permanent_naive(std::span<const double> matrix, std::size_t n) {
    if (matrix.size() < n * n || n == 0) {
        return 0.0;
    }

    std::vector<std::size_t> p(n);
    std::iota(p.begin(), p.end(), 0);

    double total_sum = 0.0;

    do {
        double current_prod = 1.0;
        for (std::size_t i = 0; i < n; ++i) {
            current_prod *= matrix[i * n + p[i]];
        }
        total_sum += current_prod;
    } while (std::next_permutation(p.begin(), p.end()));

    return total_sum;
}

} // namespace math
