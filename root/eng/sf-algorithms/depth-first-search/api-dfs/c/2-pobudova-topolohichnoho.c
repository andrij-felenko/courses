// C-реалізація топологічного сортування
typedef struct {
    int* order;
    int index;
} topo_sort_context_t;

void on_finish_vertex_topo_c(int u, int finish_time, void* user_data) {
    topo_sort_context_t* ctx = (topo_sort_context_t*)user_data;
    ctx->order[ctx->index--] = u; // Заповнюємо масив з кінця
}
