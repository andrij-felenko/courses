#include <stdio.h>
#include <stdlib.h>

typedef struct {
    int num_vertices;
    int num_edges;
    int* offset; // Розмір num_vertices + 1
    int* target; // Розмір num_edges
} csr_graph_c;

void dfs_csr_c(const csr_graph_c* g, int start) {
    int n = g->num_vertices;
    int* color = (int*)calloc(n, sizeof(int));
    int* stack = (int*)malloc(n * sizeof(int));
    int top = -1;

    color[start] = 1; // GRAY
    stack[++top] = start;

    while (top >= 0) {
        int u = stack[top--];
        color[u] = 2; // BLACK

        int start_idx = g->offset[u];
        int end_idx = g->offset[u + 1];

        for (int i = start_idx; i < end_idx; i++) {
            int v = g->target[i];
            if (color[v] == 0) { // WHITE
                color[v] = 1;
                stack[++top] = v;
            }
        }
    }

    free(color);
    free(stack);
}
