#include <stdio.h>
#include <stdbool.h>
#include <stdlib.h>

typedef struct {
    int target;
    int target_distance;
    int* dist;
    bool found;
} SearchContextC;

static void c_on_start(int u, void* user_data) {
    SearchContextC* ctx = (SearchContextC*)user_data;
    ctx->dist[u] = 0;
}

static void c_on_tree_edge(int u, int v, void* user_data) {
    SearchContextC* ctx = (SearchContextC*)user_data;
    ctx->dist[v] = ctx->dist[u] + 1;
    if (v == ctx->target) {
        ctx->target_distance = ctx->dist[v];
        ctx->found = true;
    }
}

int find_shortest_distance_c(
    int num_vertices,
    const int* const* adj_lists,
    const int* adj_sizes,
    int start,
    int target
) {
    int* dist = (int*)malloc(sizeof(int) * num_vertices);
    for (int i = 0; i < num_vertices; ++i) dist[i] = -1;

    SearchContextC ctx = {target, -1, dist, false};
    BFSVisitorC visitor = {0};
    visitor.user_data = &ctx;
    visitor.start_vertex = c_on_start;
    visitor.tree_edge = c_on_tree_edge;

    c_bfs_run(num_vertices, adj_lists, adj_sizes, start, &visitor);

    int res = ctx.found ? ctx.target_distance : -1;
    free(dist);
    return res;
}
