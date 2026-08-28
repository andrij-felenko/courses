// C-реалізація обчислення мостів та lowlink
typedef struct {
    int* d;
    int* low;
    int timer;
    bool* is_bridge_edge;
} bridge_context_t;

void on_discover_bridge_c(int u, int discovery_time, void* user_data) {
    bridge_context_t* ctx = (bridge_context_t*)user_data;
    ctx->d[u] = discovery_time;
    ctx->low[u] = discovery_time;
}

void on_finish_edge_bridge_c(int u, int v, void* user_data) {
    bridge_context_t* ctx = (bridge_context_t*)user_data;
    if (ctx->low[v] < ctx->low[u]) {
        ctx->low[u] = ctx->low[v];
    }
    if (ctx->low[v] > ctx->d[u]) {
        // Ребро (u, v) є мостом!
    }
}
