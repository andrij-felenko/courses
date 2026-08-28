#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

typedef struct {
    int u;
    int v;
} EdgeC;

// Алгоритм Уїлсона мовою C
EdgeC* wilson_ust_c(const GraphC* g, int* out_edges_count) {
    int n = g->num_vertices;
    bool* in_tree = (bool*)calloc(n, sizeof(bool));
    int* next = (int*)malloc(n * sizeof(int));
    for (int i = 0; i < n; i++) next[i] = -1;

    // Включаємо вершину 0 у дерево
    in_tree[0] = true;
    int tree_size = 1;

    for (int i = 1; i < n; i++) {
        int u = i;
        while (!in_tree[u]) {
            int deg = g->degrees[u];
            int r = rand() % deg;
            int v = g->adj[u][r];
            next[u] = v; // Крок блукача (автоматично стирає попередні цикли!)
            u = v;
        }

        // Додаємо вилучений від циклів шлях до дерева
        u = i;
        while (!in_tree[u]) {
            in_tree[u] = true;
            u = next[u];
            tree_size++;
        }
    }

    EdgeC* tree = (EdgeC*)malloc((n - 1) * sizeof(EdgeC));
    int idx = 0;
    for (int i = 1; i < n; i++) {
        tree[idx].u = i;
        tree[idx].v = next[i];
        idx++;
    }

    *out_edges_count = n - 1;
    free(in_tree);
    free(next);
    return tree;
}
