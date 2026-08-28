/* C Implementation: Kuhn's Algorithm for Maximum Bipartite Matching */
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>

typedef struct {
    int n1; // Розмір лівої частки U
    int n2; // Розмір правої частки V
    int **adj;
    int *deg;
    int *capacity;
} BipartiteGraph;

BipartiteGraph* bg_create(int n1, int n2) {
    BipartiteGraph *g = (BipartiteGraph*)malloc(sizeof(BipartiteGraph));
    if (!g) return NULL;
    g->n1 = n1;
    g->n2 = n2;
    g->adj = (int**)malloc(n1 * sizeof(int*));
    g->deg = (int*)calloc(n1, sizeof(int));
    g->capacity = (int*)malloc(n1 * sizeof(int));
    for (int i = 0; i < n1; i++) {
        g->capacity[i] = 4;
        g->adj[i] = (int*)malloc(g->capacity[i] * sizeof(int));
    }
    return g;
}

void bg_add_edge(BipartiteGraph *g, int u_left, int v_right) {
    if (g->deg[u_left] >= g->capacity[u_left]) {
        g->capacity[u_left] *= 2;
        g->adj[u_left] = (int*)realloc(g->adj[u_left], g->capacity[u_left] * sizeof(int));
    }
    g->adj[u_left][g->deg[u_left]++] = v_right;
}

static bool try_kuhn(int u, const BipartiteGraph *g, bool *visited, int *match_v) {
    if (visited[u]) return false;
    visited[u] = true;

    for (int i = 0; i < g->deg[u]; i++) {
        int v = g->adj[u][i];
        if (match_v[v] < 0 || try_kuhn(match_v[v], g, visited, match_v)) {
            match_v[v] = u;
            return true;
        }
    }
    return false;
}

int max_bipartite_matching_c(const BipartiteGraph *g, int *match_v) {
    for (int i = 0; i < g->n2; i++) {
        match_v[i] = -1;
    }

    bool *visited = (bool*)malloc(g->n1 * sizeof(bool));
    if (!visited) return 0;
    int result = 0;

    for (int u = 0; u < g->n1; u++) {
        memset(visited, 0, g->n1 * sizeof(bool));
        if (try_kuhn(u, g, visited, match_v)) {
            result++;
        }
    }

    free(visited);
    return result;
}

void bg_free(BipartiteGraph *g) {
    if (!g) return;
    for (int i = 0; i < g->n1; i++) {
        free(g->adj[i]);
    }
    free(g->adj);
    free(g->deg);
    free(g->capacity);
    free(g);
}
