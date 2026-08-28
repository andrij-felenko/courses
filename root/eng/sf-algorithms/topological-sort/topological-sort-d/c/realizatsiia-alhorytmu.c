/* Реалізація алгоритму Кана мовою C.
   Граф подано списком суміжності через масиви динамічної довжини. */
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

typedef struct {
    int* edges;
    int size;
    int capacity;
} AdjList;

bool kahn_topological_sort(int num_nodes, AdjList* adj, int* result_order) {
    int* in_degree = (int*)calloc(num_nodes, sizeof(int));
    if (!in_degree) return false;

    // 1. Обчислення вхідних степеней вершин
    for (int u = 0; u < num_nodes; u++) {
        for (int i = 0; i < adj[u].size; i++) {
            int v = adj[u].edges[i];
            in_degree[v]++;
        }
    }

    // 2. Ініціалізація черги (на основі звичайного масиву з вказівниками head/tail)
    int* queue = (int*)malloc(num_nodes * sizeof(int));
    int head = 0, tail = 0;
    for (int i = 0; i < num_nodes; i++) {
        if (in_degree[i] == 0) {
            queue[tail++] = i;
        }
    }

    // 3. Основний цикл обробки джерел
    int result_index = 0;
    while (head < tail) {
        int u = queue[head++];
        result_order[result_index++] = u;

        for (int i = 0; i < adj[u].size; i++) {
            int v = adj[u].edges[i];
            in_degree[v]--;
            if (in_degree[v] == 0) {
                queue[tail++] = v;
            }
        }
    }

    free(in_degree);
    free(queue);

    // Якщо оброблено всі вершини — циклів немає
    return (result_index == num_nodes);
}
