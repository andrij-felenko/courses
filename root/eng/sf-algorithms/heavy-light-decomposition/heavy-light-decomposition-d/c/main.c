int find_lca(const hld_tree_t *tree, int u, int v) {
    while (tree->head[u] != tree->head[v]) {
        if (tree->depth[tree->head[u]] > tree->depth[tree->head[v]]) {
            u = tree->parent[tree->head[u]];
        } else {
            v = tree->parent[tree->head[v]];
        }
    }
    return tree->depth[u] < tree->depth[v] ? u : v;
}
