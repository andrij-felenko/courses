/* C Implementation: BFS 2-coloring for Bipartite Verification */
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

typedef struct {
    int num_vertices;
    int **adj;
    int *deg;
    int *capacity;
} Graph;

Graph* graph_create(int n) {
    Graph *g = (Graph*)malloc(sizeof(Graph));
    if (!g) return NULL;
    g->num_vertices = n;
    g->adj = (int**)malloc(n * sizeof(int*));
    g->deg = (int*)calloc(n, sizeof(int));
    g->capacity = (int*)malloc(n * sizeof(int));
    for (int i = 0; i < n; i++) {
        g->capacity[i] = 4;
        g->adj[i] = (int*)malloc(g->capacity[i] * sizeof(int));
    }
    return g;
}

void graph_add_edge(Graph *g, int u, int v) {
    if (g->deg[u] >= g->capacity[u]) {
        g->capacity[u] *= 2;
        g->adj[u] = (int*)realloc(g->adj[u], g->capacity[u] * sizeof(int));
    }
    g->adj[u][g->deg[u]++] = v;

    if (g->deg[v] >= g->capacity[v]) {
        g->capacity[v] *= 2;
        g->adj[v] = (int*)realloc(g->adj[v], g->capacity[v] * sizeof(int));
    }
    g->adj[v][g->deg[v]++] = u;
}

void graph_free(Graph *g) {
    if (!g) return;
    for (int i = 0; i < g->num_vertices; i++) {
        free(g->adj[i]);
    }
    free(g->adj);
    free(g->deg);
    free(g->capacity);
    free(g);
}

// Повертає true, якщо граф двочастковий; заповнює масив colors (0 або 1, -1 якщо непризначено)
bool check_bipartite_c(const Graph *g, int *colors) {
    int n = g->num_vertices;
    for (int i = 0; i < n; i++) {
        colors[i] = -1;
    }

    int *queue = (int*)malloc(n * sizeof(int));
    if (!queue) return false;

    for (int start = 0; start < n; start++) {
        if (colors[start] != -1) continue;

        int head = 0, tail = 0;
        colors[start] = 0;
        queue[tail++] = start;

        while (head < tail) {
            int u = queue[head++];
            int current_color = colors[u];
            int next_color = 1 - current_color;

            for (int i = 0; i < g->deg[u]; i++) {
                int v = g->adj[u][i];
                if (colors[v] == -1) {
                    colors[v] = next_color;
                    queue[tail++] = v;
                } else if (colors[v] == current_color) {
                    free(queue);
                    return false; // Конфлікт розфарбування (знайдено непарний цикл)
                }
            }
        }
    }

    free(queue);
    return true;
}
