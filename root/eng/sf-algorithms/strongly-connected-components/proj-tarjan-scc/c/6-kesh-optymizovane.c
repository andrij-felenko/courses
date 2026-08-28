typedef struct {
    int num_vertices;
    int num_edges;
    int* row_ptr; /* Масив розміром V + 1 зі зсувами для кожної вершини */
    int* cols;    /* Плаский масив мети ребер розміром E */
} CSRGraph;

void tarjan_csr_c(const CSRGraph* g) {
    int n = g->num_vertices;
    int* tin = (int*)calloc(n, sizeof(int));
    int* low = (int*)calloc(n, sizeof(int));
    bool* in_stack = (bool*)calloc(n, sizeof(bool));
    int* stack = (int*)malloc(n * sizeof(int));
    int top = -1, timer = 0;

    for (int i = 0; i < n; i++) {
        if (tin[i] == 0) {
            /* Запуск обходу з вершини i */
        }
    }

    free(tin); free(low); free(in_stack); free(stack);
}
