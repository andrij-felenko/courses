template <typename ValueType>
ValueType query_edge_path_custom(HeavyLightDecomposition<ValueType>& hld, int u, int v) {
    ValueType sum{0};
    int lca = hld.find_lca(u, v);
    // Обчислення реберного запиту з виключенням вершини LCA
    if (u != lca) {
        sum += hld.query_path(u, lca);
    }
    if (v != lca) {
        sum += hld.query_path(v, lca);
    }
    return sum;
}
