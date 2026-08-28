static int64_t hld_query_edge_path(HLDTree *tree, int u, int v) {
    int64_t sum = 0;
    while (tree->head[u] != tree->head[v]) {
        if (tree->depth[tree->head[u]] < tree->depth[tree->head[v]]) {
            int tmp = u; u = v; v = tmp;
        }
        sum += seg_query(tree, 0, 0, tree->n - 1, tree->pos[tree->head[u]], tree->pos[u]);
        u = tree->parent[tree->head[u]];
    }
    if (u == v) return sum;
    if (tree->depth[u] > tree->depth[v]) {
        int tmp = u; u = v; v = tmp;
    }
    sum += seg_query(tree, 0, 0, tree->n - 1, tree->pos[u] + 1, tree->pos[v]);
    return sum;
}
