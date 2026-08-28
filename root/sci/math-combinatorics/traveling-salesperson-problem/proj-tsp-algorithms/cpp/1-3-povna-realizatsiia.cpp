#include <vector>
#include <limits>
#include <cstdint>
#include <algorithm>

struct TspResult {
    double min_cost{std::numeric_limits<double>::infinity()};
    std::vector<size_t> path;
};

/**
 * Ідіоматична реалізація алгоритму Хелда-Карпа на C++ з використанням std::vector.
 */
TspResult tsp_held_karp_cpp(const std::vector<std::vector<double>>& matrix) {
    const size_t n = matrix.size();
    if (n == 0 || n > 20) return {};

    const uint32_t num_states = 1U << n;
    constexpr double inf = std::numeric_limits<double>::infinity();

    /* Таблиця DP розміром (2^n) x n з автоматичним очищенням пам'яті */
    std::vector<std::vector<double>> dp(num_states, std::vector<double>(n, inf));
    std::vector<std::vector<int>> parent(num_states, std::vector<int>(n, -1));

    dp[1U << 0][0] = 0.0;

    for (uint32_t mask = 1; mask < num_states; ++mask) {
        if (!(mask & 1U)) continue;

        for (size_t u = 0; u < n; ++u) {
            if (!(mask & (1U << u))) continue;
            if (dp[mask][u] == inf) continue;

            for (size_t v = 0; v < n; ++v) {
                if (mask & (1U << v)) continue;

                uint32_t next_mask = mask | (1U << v);
                double new_cost = dp[mask][u] + matrix[u][v];

                if (new_cost < dp[next_mask][v]) {
                    dp[next_mask][v] = new_cost;
                    parent[next_mask][v] = static_cast<int>(u);
                }
            }
        }
    }

    uint32_t full_mask = (1U << n) - 1;
    TspResult result;
    size_t last_node = 0;

    for (size_t u = 1; u < n; ++u) {
        if (dp[full_mask][u] == inf) continue;
        double total = dp[full_mask][u] + matrix[u][0];
        if (total < result.min_cost) {
            result.min_cost = total;
            last_node = u;
        }
    }

    if (result.min_cost == inf) return result;

    /* Зворотний трекінг для відновлення гамільтонового циклу */
    result.path.resize(n + 1);
    uint32_t curr_mask = full_mask;
    size_t curr_node = last_node;

    for (int i = static_cast<int>(n) - 1; i >= 1; --i) {
        result.path[i] = curr_node;
        int prev = parent[curr_mask][curr_node];
        curr_mask ^= (1U << curr_node);
        curr_node = static_cast<size_t>(prev);
    }
    result.path[0] = 0;
    result.path[n] = 0;

    return result;
}
