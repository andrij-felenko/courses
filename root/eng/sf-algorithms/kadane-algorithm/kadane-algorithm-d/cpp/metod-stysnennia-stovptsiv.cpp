#include <vector>
#include <algorithm>
#include <cstddef>

[[nodiscard]] long long kadane_2d(const std::vector<std::vector<int>>& matrix) {
    if (matrix.empty() || matrix[0].empty()) {
        return 0;
    }

    const std::size_t rows = matrix.size();
    const std::size_t cols = matrix[0].size();
    std::vector<int> col_sum(cols, 0);
    long long global_max = matrix[0][0];

    for (std::size_t r1 = 0; r1 < rows; ++r1) {
        std::fill(col_sum.begin(), col_sum.end(), 0);

        for (std::size_t r2 = r1; r2 < rows; ++r2) {
            for (std::size_t c = 0; c < cols; ++c) {
                col_sum[c] += matrix[r2][c];
            }

            long long current_sum = col_sum[0];
            long long local_max = col_sum[0];

            for (std::size_t c = 1; c < cols; ++c) {
                current_sum = std::max<long long>(col_sum[c], current_sum + col_sum[c]);
                local_max = std::max(local_max, current_sum);
            }

            if (r1 == 0 && r2 == 0) {
                global_max = local_max;
            } else {
                global_max = std::max(global_max, local_max);
            }
        }
    }

    return global_max;
}
