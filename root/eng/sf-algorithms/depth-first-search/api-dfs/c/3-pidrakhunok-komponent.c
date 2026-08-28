// C-реалізація розмітки компонент
typedef struct {
    int current_component;
    int* component_map;
} component_context_t;

void on_start_vertex_c(int u, void* user_data) {
    component_context_t* ctx = (component_context_t*)user_data;
    ctx->current_component++;
}

void on_discover_vertex_comp_c(int u, int d_time, void* user_data) {
    component_context_t* ctx = (component_context_t*)user_data;
    ctx->component_map[u] = ctx->current_component;
}
