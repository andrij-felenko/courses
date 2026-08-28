/* Перевірка консервативного критерію Джорджа для злиття v1 та v2 */
bool can_coalesce_george(size_t v1, size_t v2, size_t K, 
                         const std::vector<std::vector<bool>>& adj, 
                         const std::vector<int>& degree) {
    const size_t n = adj.size();
    for (size_t t = 0; t < n; ++t) {
        if (adj[v1][t]) { // For every neighbor t of v1
            // Condition: t must already interfere with v2 OR deg(t) < K
            bool interferes_with_v2 = adj[v2][t];
            bool low_degree = static_cast<size_t>(degree[t]) < K;
            if (!interferes_with_v2 && !low_degree) {
                return false; // Coalescing unsafe!
            }
        }
    }
    return true; // Coalescing safe
}
