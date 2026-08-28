#include <stdlib.h>

typedef struct {
    int current_component;
    int* component_map;
} ComponentContextC;

static void c_on_discover_comp(int u, void* user_data) {
    ComponentContextC* ctx = (ComponentContextC*)user_data;
    ctx->component_map[u] = ctx->current_component;
}

void compute_components_c(
    int num_vertices,
    const int* const* adj_lists,
    const int* adj_sizes,
    int* out_components
) {
    for (int i = 0; i < num_vertices; ++i) out_components[i] = -1;

    ComponentContextC ctx = {0, out_components};
    BFSVisitorC visitor = {0};
    visitor.user_data = &ctx;
    visitor.discover_vertex = c_on_discover_comp;

    int comp_id = 0;
    for (int i = 0; i < num_vertices; ++i) {
        if (out_components[i] == -1) {
            ctx.current_component = comp_id++;
            c_bfs_run(num_vertices, adj_lists, adj_sizes, i, &visitor);
        }
    }
}
