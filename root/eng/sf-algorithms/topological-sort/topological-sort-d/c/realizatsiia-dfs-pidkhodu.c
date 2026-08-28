/* Реалізація топологічного сортування через DFS мовою C.
   Використовує 3 кольори вершин (0 - WHITE, 1 - GRAY, 2 - BLACK). */
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

#define COLOR_WHITE 0
#define COLOR_GRAY  1
#define COLOR_BLACK 2

typedef struct {
    int* edges;
    int size;
} AdjListDFS;

static bool dfs_visit(int u, AdjListDFS* adj, int* color, int* stack, int* stack_idx) {
    color[u] = COLOR_GRAY;

    for (int i = 0; i < adj[u].size; i++) {
        int v = adj[u].edges[i];
        if (color[v] == COLOR_GRAY) {
            return false; // Знайдено зворотне ребро -> ЦИКЛ!
        }
        if (color[v] == COLOR_WHITE) {
            if (!dfs_visit(v, adj, color, stack, stack_idx)) {
                return false;
            }
        }
    }

    color[u] = COLOR_BLACK;
    stack[(*stack_idx)++] = u; // Записуємо в момент виходу (post-order)
    return true;
}

bool dfs_topological_sort(int num_nodes, AdjListDFS* adj, int* result_order) {
    int* color = (int*)calloc(num_nodes, sizeof(int));
    int* stack = (int*)malloc(num_nodes * sizeof(int));
    int stack_idx = 0;

    for (int i = 0; i < num_nodes; i++) {
        if (color[i] == COLOR_WHITE) {
            if (!dfs_visit(i, adj, color, stack, &stack_idx)) {
                free(color);
                free(stack);
                return false; // Граф містить цикл
            }
        }
    }

    // Розвертаємо стек у підсумковий масив
    for (int i = 0; i < num_nodes; i++) {
        result_order[i] = stack[num_nodes - 1 - i];
    }

    free(color);
    free(stack);
    return true;
}
