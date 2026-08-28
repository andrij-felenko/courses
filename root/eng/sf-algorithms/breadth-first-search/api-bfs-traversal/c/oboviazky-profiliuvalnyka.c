#include <stdbool.h>
#include <stdlib.h>

typedef struct {
    size_t current_queue_size;
    size_t peak_queue_size;
    size_t total_edges_examined;
} MemoryProfileContextC;

static void c_on_discover_profile(int u, void* user_data) {
    MemoryProfileContextC* ctx = (MemoryProfileContextC*)user_data;
    ctx->current_queue_size++;
    if (ctx->current_queue_size > ctx->peak_queue_size) {
        ctx->peak_queue_size = ctx->current_queue_size;
    }
}

static void c_on_examine_vertex_profile(int u, void* user_data) {
    MemoryProfileContextC* ctx = (MemoryProfileContextC*)user_data;
    if (ctx->current_queue_size > 0) {
        ctx->current_queue_size--;
    }
}

static void c_on_examine_edge_profile(int u, int v, void* user_data) {
    MemoryProfileContextC* ctx = (MemoryProfileContextC*)user_data;
    ctx->total_edges_examined++;
}

void profile_bfs_c(
    int num_vertices,
    const int* const* adj_lists,
    const int* adj_sizes,
    int start,
    size_t* out_peak_queue,
    size_t* out_total_edges
) {
    MemoryProfileContextC ctx = {0, 0, 0};
    BFSVisitorC visitor = {0};
    visitor.user_data = &ctx;
    visitor.discover_vertex = c_on_discover_profile;
    visitor.examine_vertex = c_on_examine_vertex_profile;
    visitor.examine_edge = c_on_examine_edge_profile;

    c_bfs_run(num_vertices, adj_lists, adj_sizes, start, &visitor);

    *out_peak_queue = ctx.peak_queue_size;
    *out_total_edges = ctx.total_edges_examined;
}
