void tc_incremental_add_edge(bool *T, size_t V, size_t u, size_t v) {
    if (T[u * V + v]) return;

    T[u * V + v] = true;

    for (size_t i = 0; i < V; ++i) {
        if (i == u || T[i * V + u]) {
            for (size_t j = 0; j < V; ++j) {
                if (j == v || T[v * V + j]) {
                    T[i * V + j] = true;
                }
            }
        }
    }
}
