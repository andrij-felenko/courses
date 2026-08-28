#include <vector>
#include <optional>
#include <span>
#include <cstddef>
#include <algorithm>

struct MatrixSubarrayResult {
    long long max_sum{0};
    std::size_t top_row{0};
    std::size_t bottom_row{0};
    std::size_t left_col{0};
    std::size_t right_col{0};
};

[[nodiscard]] std::optional<MatrixSubarrayResult> kadane_2d_matrix(
    const std::vector<std::vector<int>>& matrix) {
    if (matrix.empty() || matrix[0].empty()) {
        return std::nullopt;
    }

    const std::size_t rows = matrix.size();
    const std::size_t cols = matrix[0].size();

    std::vector<int> col_sum(cols, 0);
    long long global_max = matrix[0][0];
    std::size_t best_r1 = 0, best_r2 = 0, best_c1 = 0, best_c2 = 0;

    for (std::size_t r1 = 0; r1 < rows; ++r1) {
        std::fill(col_sum.begin(), col_sum.end(), 0);

        for (std::size_t r2 = r1; r2 < rows; ++r2) {
            for (std::size_t c = 0; c < cols; ++c) {
                col_sum[c] += matrix[r2][c];
            }

            long long current_sum = col_sum[0];
            long long local_max = col_sum[0];
            std::size_t current_c1 = 0;
            std::size_t local_c1 = 0, local_c2 = 0;

            for (std::size_t c = 1; c < cols; ++c) {
                if (current_sum < 0) {
                    current_sum = col_sum[c];
                    current_c1 = c;
                } else {
                    current_sum += col_sum[c];
                }

                if (current_sum > local_max) {
                    local_max = current_sum;
                    local_c1 = current_c1;
                    local_c2 = c;
                }
            }

            if (r1 == 0 && r2 == 0) {
                global_max = local_max;
                best_r1 = r1; best_r2 = r2;
                best_c1 = local_c1; best_c2 = local_c2;
            } else if (local_max > global_max) {
                global_max = local_max;
                best_r1 = r1;
                best_r2 = r2;
                best_c1 = local_c1;
                best_c2 = local_c2;
            }
        }
    }

    return MatrixSubarrayResult{
        .max_sum = global_max,
        .top_row = best_r1,
        .bottom_row = best_r2,
        .left_col = best_c1,
        .right_col = best_c2
    };
}
