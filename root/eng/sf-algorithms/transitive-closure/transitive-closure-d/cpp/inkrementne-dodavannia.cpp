void tcIncrementalAddEdge(std::vector<uint8_t>& T, size_t V, size_t u, size_t v) {
    if (T[u * V + v]) return;

    T[u * V + v] = 1;

    for (size_t i = 0; i < V; ++i) {
        if (i == u || T[i * V + u]) {
            const size_t i_off = i * V;
            const size_t v_off = v * V;
            for (size_t j = 0; j < V; ++j) {
                if (j == v || T[v_off + j]) {
                    T[i_off + j] = 1;
                }
            }
        }
    }
}
