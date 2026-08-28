// C-реалізація детектора циклів через контекст
typedef struct {
    bool has_cycle;
    int cycle_u;
    int cycle_v;
} cycle_detector_context_t;

void on_back_edge_c(int u, int v, void* user_data) {
    cycle_detector_context_t* ctx = (cycle_detector_context_t*)user_data;
    ctx->has_cycle = true;
    ctx->cycle_u = u;
    ctx->cycle_v = v;
}
