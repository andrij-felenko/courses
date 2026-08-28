#include <iostream>
#include <vector>
#include <cstdint>
#include <limits>
#include <span>
#include <algorithm>
#include <stdexcept>

enum class HungarianObjective {
    Minimize,
    Maximize
};

struct HungarianSolution {
    int64_t total_cost{0};
    std::vector<int32_t> assignment; // assignment[i] = стовпець для рядка i
};

class HungarianDenseSolver {
public:
    static constexpr int64_t INF = std::numeric_limits<int64_t>::max() / 4;

    static HungarianSolution solve(
        std::span<const int64_t> cost_matrix,
        int32_t rows,
        int32_t cols,
        HungarianObjective objective = HungarianObjective::Minimize
    ) {
        if (rows <= 0 || cols <= 0) {
            throw std::invalid_argument("Matrix dimensions must be positive");
        }
        if (cost_matrix.size() != static_cast<size_t>(rows) * cols) {
            throw std::invalid_argument("Flat matrix size must match rows * cols");
        }
        if (rows > cols) {
            throw std::invalid_argument("Hungarian algorithm requires rows <= cols");
        }

        std::vector<int64_t> work(cost_matrix.begin(), cost_matrix.end());
        if (objective == HungarianObjective::Maximize) {
            const int64_t max_val = *std::max_element(work.begin(), work.end());
            for (auto& val : work) {
                val = max_val - val;
            }
        }

        std::vector<int64_t> u(rows + 1, 0);
        std::vector<int64_t> v(cols + 1, 0);
        std::vector<int32_t> p(cols + 1, 0);
        std::vector<int32_t> way(cols + 1, 0);
        std::vector<int64_t> minv(cols + 1);
        std::vector<uint8_t> used(cols + 1);

        for (int32_t i = 1; i <= rows; ++i) {
            p[0] = i;
            int32_t j0 = 0;
            std::fill(minv.begin(), minv.end(), INF);
            std::fill(used.begin(), used.end(), 0);

            do {
                used[j0] = 1;
                const int32_t i0 = p[j0];
                int64_t delta = INF;
                int32_t j1 = 0;

                for (int32_t j = 1; j <= cols; ++j) {
                    if (!used[j]) {
                        const int64_t cur = work[(i0 - 1) * cols + (j - 1)] - u[i0] - v[j];
                        if (cur < minv[j]) {
                            minv[j] = cur;
                            way[j] = j0;
                        }
                        if (minv[j] < delta) {
                            delta = minv[j];
                            j1 = j;
                        }
                    }
                }

                for (int32_t j = 0; j <= cols; ++j) {
                    if (used[j]) {
                        u[p[j]] += delta;
                        v[j] -= delta;
                    } else {
                        minv[j] -= delta;
                    }
                }
                j0 = j1;
            } while (p[j0] != 0);

            do {
                const int32_t j1 = way[j0];
                p[j0] = p[j1];
                j0 = j1;
            } while (j0 != 0);
        }

        HungarianSolution result;
        result.assignment.assign(rows, -1);
        for (int32_t j = 1; j <= cols; ++j) {
            if (p[j] > 0 && p[j] <= rows) {
                result.assignment[p[j] - 1] = j - 1;
            }
        }

        int64_t total = 0;
        for (int32_t i = 0; i < rows; ++i) {
            if (result.assignment[i] >= 0) {
                total += cost_matrix[i * cols + result.assignment[i]];
            }
        }
        result.total_cost = total;
        return result;
    }
};

int main() {
    constexpr int32_t N = 3, M = 3;
    const std::vector<int64_t> costs = {
        10, 19, 8,
        10, 18, 7,
        13, 16, 9
    };

    const auto sol = HungarianDenseSolver::solve(costs, N, M, HungarianObjective::Minimize);
    std::cout << "Total min cost: " << sol.total_cost << "\n";
    for (int32_t i = 0; i < N; ++i) {
        std::cout << "Row " << i << " -> Col " << sol.assignment[i]
                  << " (cost " << costs[i * M + sol.assignment[i]] << ")\n";
    }
    return 0;
}
