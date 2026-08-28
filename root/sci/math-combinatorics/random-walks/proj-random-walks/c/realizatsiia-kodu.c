#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdint.h>

typedef struct {
    int num_vertices;
    int num_edges;
    int** adj;
    int* degrees;
} GraphC;

GraphC* graph_create(int n) {
    GraphC* g = (GraphC*)malloc(sizeof(GraphC));
    g->num_vertices = n;
    g->num_edges = 0;
    g->degrees = (int*)calloc(n, sizeof(int));
    g->adj = (int**)malloc(n * sizeof(int*));
    for (int i = 0; i < n; i++) {
        g->adj[i] = NULL;
    }
    return g;
}

void graph_add_edge(GraphC* g, int u, int v) {
    g->degrees[u]++;
    g->adj[u] = (int*)realloc(g->adj[u], g->degrees[u] * sizeof(int));
    g->adj[u][g->degrees[u] - 1] = v;

    g->degrees[v]++;
    g->adj[v] = (int*)realloc(g->adj[v], g->degrees[v] * sizeof(int));
    g->adj[v][g->degrees[v] - 1] = u;

    g->num_edges++;
}

void graph_free(GraphC* g) {
    for (int i = 0; i < g->num_vertices; i++) {
        free(g->adj[i]);
    }
    free(g->adj);
    free(g->degrees);
    free(g);
}

// Імовірнісна перевірка s-t зв'язності (O(1) додаткової пам'яті окрім графа)
bool random_walk_st_connectivity(const GraphC* g, int s, int t, int max_runs) {
    if (s == t) return true;
    if (g->degrees[s] == 0 || g->degrees[t] == 0) return false;

    // Теоретична межа кроків: 2 * m * n
    long long max_steps = 2LL * g->num_edges * g->num_vertices;

    for (int run = 0; run < max_runs; run++) {
        int current = s;
        for (long long step = 0; step < max_steps; step++) {
            int deg = g->degrees[current];
            int next_idx = rand() % deg;
            current = g->adj[current][next_idx];

            if (current == t) {
                return true; // Шлях знайдено!
            }
        }
    }
    return false; // Шлях з високою ймовірністю відсутній
}
