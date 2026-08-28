// Виклик події в мові C за допомогою безпечного макросу
#define DFS_NOTIFY(event, ...) \
    do { \
        if (visitor && visitor->event) { \
            visitor->event(__VA_ARGS__, user_data); \
        } \
    } while(0)

static void dfs_internal_visit_c(const dfs_graph_t* g, int u, int* color, 
                                int* d, int* f, int* timer, 
                                const dfs_visitor_t* visitor, void* user_data) {
    color[u] = 1; // GRAY
    d[u] = ++(*timer);
    DFS_NOTIFY(discover_vertex, u, d[u]);

    for (int v = 0; v < g->num_vertices; v++) {
        if (g->adj_matrix[u][v]) {
            DFS_NOTIFY(examine_edge, u, v);
            if (color[v] == 0) { // WHITE
                DFS_NOTIFY(tree_edge, u, v);
                dfs_internal_visit_c(g, v, color, d, f, timer, visitor, user_data);
                DFS_NOTIFY(finish_edge, u, v);
            } else if (color[v] == 1) { // GRAY
                DFS_NOTIFY(back_edge, u, v);
            } else { // BLACK
                DFS_NOTIFY(forward_or_cross_edge, u, v);
            }
        }
    }

    color[u] = 2; // BLACK
    f[u] = ++(*timer);
    DFS_NOTIFY(finish_vertex, u, f[u]);
}
