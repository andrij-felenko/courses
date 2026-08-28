/* Нерекурсивна реалізація DFS топологічного сортування мовою C.
   Використовує явний стек у купі замість системного стеку викликів. */
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

bool iterative_dfs_topological_sort(int num_nodes, AdjListDFS* adj, int* result_order) {
    int* color = (int*)calloc(num_nodes, sizeof(int));
    int* edge_idx = (int*)calloc(num_nodes, sizeof(int));
    int* stack = (int*)malloc(num_nodes * sizeof(int));
    int* finish_order = (int*)malloc(num_nodes * sizeof(int));
    int stack_top = 0;
    int finish_idx = 0;

    for (int i = 0; i < num_nodes; i++) {
        if (color[i] != 0) continue;

        stack[stack_top++] = i;
        color[i] = 1; // Gray

        while (stack_top > 0) {
            int u = stack[stack_top - 1];

            if (edge_idx[u] < adj[u].size) {
                int v = adj[u].edges[edge_idx[u]++];

                if (color[v] == 1) {
                    // Звільняємо пам'ять та повертаємо false (знайдено цикл)
                    free(color); free(edge_idx); free(stack); free(finish_order);
                    return false;
                }
                if (color[v] == 0) {
                    color[v] = 1;
                    stack[stack_top++] = v;
                }
            } else {
                color[u] = 2; // Black
                finish_order[finish_idx++] = u;
                stack_top--;
            }
        }
    }

    for (int i = 0; i < num_nodes; i++) {
        result_order[i] = finish_order[num_nodes - 1 - i];
    }

    free(color); free(edge_idx); free(stack); free(finish_order);
    return true;
}
