#include <stdbool.h>
#include <stdlib.h>

typedef struct {
    int* color;
    bool is_bipartite;
} BipartiteContextC;

static void c_on_start_bipartite(int u, void* user_data) {
    BipartiteContextC* ctx = (BipartiteContextC*)user_data;
    ctx->color[u] = 1;
}

static void c_on_tree_edge_bipartite(int u, int v, void* user_data) {
    BipartiteContextC* ctx = (BipartiteContextC*)user_data;
    ctx->color[v] = 3 - ctx->color[u];
}

static void c_on_non_tree_edge_bipartite(int u, int v, void* user_data) {
    BipartiteContextC* ctx = (BipartiteContextC*)user_data;
    if (ctx->color[u] == ctx->color[v]) {
        ctx->is_bipartite = false;
    }
}

bool check_bipartite_c(
    int num_vertices,
    const int* const* adj_lists,
    const int* adj_sizes
) {
    int* color = (int*)calloc(num_vertices, sizeof(int));
    BipartiteContextC ctx = {color, true};
    BFSVisitorC visitor = {0};
    visitor.user_data = &ctx;
    visitor.start_vertex = c_on_start_bipartite;
    visitor.tree_edge = c_on_tree_edge_bipartite;
    visitor.non_tree_edge = c_on_non_tree_edge_bipartite;

    for (int i = 0; i < num_vertices; ++i) {
        if (color[i] == 0) {
            c_bfs_run(num_vertices, adj_lists, adj_sizes, i, &visitor);
        }
    }

    bool res = ctx.is_bipartite;
    free(color);
    return res;
}
