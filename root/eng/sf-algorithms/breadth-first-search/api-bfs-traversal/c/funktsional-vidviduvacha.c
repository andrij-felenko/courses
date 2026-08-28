#include <stdio.h>
#include <stdlib.h>

typedef struct {
    int max_degree;
    long long total_degree;
    int vertices_count;
} DegreeStatsContextC;

static void c_on_examine_vertex_degree(int u, void* user_data) {
    DegreeStatsContextC* ctx = (DegreeStatsContextC*)user_data;
    ctx->vertices_count++;
}

void analyze_degrees_c(
    int num_vertices,
    const int* const* adj_lists,
    const int* adj_sizes,
    int start
) {
    DegreeStatsContextC ctx = {0, 0, 0};
    BFSVisitorC visitor = {0};
    visitor.user_data = &ctx;
    visitor.examine_vertex = c_on_examine_vertex_degree;

    c_bfs_run(num_vertices, adj_lists, adj_sizes, start, &visitor);
    printf("Оброблено вершин: %d\n", ctx.vertices_count);
}
