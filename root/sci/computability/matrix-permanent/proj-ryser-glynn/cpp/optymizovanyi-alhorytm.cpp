#include <vector>
#include <span>
#include <cstdint>
#include <bit>
#include <stdexcept>

namespace math {

// Високоефективний C++20 алгоритм Райзера для 64-бітних цілих чисел
[[nodiscard]] std::uint64_t permanent_ryser(std::span<const std::uint64_t> matrix, std::size_t n) {
    if (n == 0 || matrix.size() < n * n) {
        return 0;
    }
    if (n > 62) {
        throw std::invalid_argument("Dimension n > 62 is too large for 64-bit mask iteration");
    }

    std::vector<std::uint64_t> row_sum(n, 0);
    std::uint64_t total_sum = 0;
    const std::uint64_t num_subsets = 1ULL << n;
    std::uint64_t prev_gray = 0;

    for (std::uint64_t i = 1; i < num_subsets; ++i) {
        const std::uint64_t gray = i ^ (i >> 1);
        const std::uint64_t diff = gray ^ prev_gray;

        const std::size_t bit_idx = static_cast<std::size_t>(std::countr_zero(diff));
        const bool is_added = (gray & diff) != 0;

        if (is_added) {
            for (std::size_t r = 0; r < n; ++r) {
                row_sum[r] += matrix[r * n + bit_idx];
            }
        } else {
            for (std::size_t r = 0; r < n; ++r) {
                row_sum[r] -= matrix[r * n + bit_idx];
            }
        }

        std::uint64_t prod = 1;
        for (std::size_t r = 0; r < n; ++r) {
            prod *= row_sum[r];
        }

        const auto subset_size = std::popcount(gray);
        if (subset_size & 1) {
            total_sum -= prod;
        } else {
            total_sum += prod;
        }

        prev_gray = gray;
    }

    if (n & 1) {
        total_sum = static_cast<std::uint64_t>(-static_cast<std::int64_t>(total_sum));
    }

    return total_sum;
}

} // namespace math
