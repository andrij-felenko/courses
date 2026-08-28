#include <vector>
#include <cstdint>
#include <limits>
#include <span>
#include <algorithm>
#include <stdexcept>

struct HungarianResult {
    int64_t total_cost{0};
    std::vector<int32_t> assignment; // assignment[row] = col
};

class HungarianSolver {
public:
    static constexpr int64_t INF = std::numeric_limits<int64_t>::max() / 4;

    static HungarianResult solve(std::span<const int64_t> flat_matrix, int32_t n) {
        if (flat_matrix.size() != static_cast<size_t>(n) * n) {
            throw std::invalid_argument("Matrix size does not match n * n dimension");
        }

        std::vector<int64_t> u(n + 1, 0);
        std::vector<int64_t> v(n + 1, 0);
        std::vector<int32_t> p(n + 1, 0);
        std::vector<int32_t> way(n + 1, 0);
        std::vector<int64_t> minv(n + 1);
        std::vector<uint8_t> used(n + 1);

        for (int32_t i = 1; i <= n; ++i) {
            p[0] = i;
            int32_t j0 = 0;
            std::fill(minv.begin(), minv.end(), INF);
            std::fill(used.begin(), used.end(), 0);

            do {
                used[j0] = 1;
                const int32_t i0 = p[j0];
                int64_t delta = INF;
                int32_t j1 = 0;

                for (int32_t j = 1; j <= n; ++j) {
                    if (!used[j]) {
                        const int64_t cur = flat_matrix[(i0 - 1) * n + (j - 1)] - u[i0] - v[j];
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

                for (int32_t j = 0; j <= n; ++j) {
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

        HungarianResult result;
        result.assignment.resize(n);
        for (int32_t j = 1; j <= n; ++j) {
            if (p[j] > 0) {
                result.assignment[p[j] - 1] = j - 1;
            }
        }
        result.total_cost = -v[0];
        return result;
    }
};
