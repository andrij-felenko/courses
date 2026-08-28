#include <vector>
#include <optional>
#include <cstdint>

class HeldKarpSolver {
public:
    static std::optional<std::vector<size_t>> solve(const Graph& graph) {
        const size_t n = graph.size();
        if (n < 3 || n > 30) return std::nullopt;

        const size_t num_states = 1ULL << n;
        std::vector<std::vector<uint8_t>> dp(num_states, std::vector<uint8_t>(n, 0));
        std::vector<std::vector<int32_t>> parent(num_states, std::vector<int32_t>(n, -1));

        dp[1][0] = 1;

        for (size_t mask = 1; mask < num_states; ++mask) {
            if (!(mask & 1)) continue;

            for (size_t v = 0; v < n; ++v) {
                if (!dp[mask][v]) continue;

                for (size_t next_v = 0; next_v < n; ++next_v) {
                    if (mask & (1ULL << next_v)) continue;
                    if (!graph.has_edge(v, next_v)) continue;

                    size_t next_mask = mask | (1ULL << next_v);
                    dp[next_mask][next_v] = 1;
                    parent[next_mask][next_v] = static_cast<int32_t>(v);
                }
            }
        }

        const size_t full_mask = num_states - 1;
        int32_t last_v = -1;

        for (size_t v = 1; v < n; ++v) {
            if (dp[full_mask][v] && graph.has_edge(v, 0)) {
                last_v = static_cast<int32_t>(v);
                break;
            }
        }

        if (last_v == -1) return std::nullopt;

        std::vector<size_t> path(n);
        size_t curr_mask = full_mask;
        size_t curr_v = static_cast<size_t>(last_v);

        for (size_t step = n - 1; step >= 1; --step) {
            path[step] = curr_v;
            int32_t prev_v = parent[curr_mask][curr_v];
            curr_mask ^= (1ULL << curr_v);
            curr_v = static_cast<size_t>(prev_v);
        }
        path[0] = 0;

        return path;
    }
};
