#include <vector>
#include <optional>
#include <iostream>
#include <cstdint>

constexpr int64_t INF = (1LL << 60);
constexpr int NIL = -1;

std::optional<std::vector<int>> reconstruct_path(int u, int v, int n, 
                                                 const std::vector<int>& next_matrix,
                                                 const std::vector<int64_t>& dist_matrix) {
    if (dist_matrix[static_cast<size_t>(u) * n + v] >= INF || 
        next_matrix[static_cast<size_t>(u) * n + v] == NIL) {
        return std::nullopt;
    }

    std::vector<int> path;
    path.push_back(u);
    int cur = u;
    int steps = 0;
    
    while (cur != v && steps < n) {
        cur = next_matrix[static_cast<size_t>(cur) * n + v];
        if (cur == NIL) return std::nullopt;
        path.push_back(cur);
        steps++;
    }
    
    if (cur != v) return std::nullopt; // виявлено зациклення
    return path;
}
