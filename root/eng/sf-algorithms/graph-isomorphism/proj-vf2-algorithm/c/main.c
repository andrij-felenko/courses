#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

typedef struct {
    int n;
    bool **adj;
} Graph;

Graph* graph_create(int n) {
    Graph *g = (Graph*)malloc(sizeof(Graph));
    g->n = n;
    g->adj = (bool**)malloc(n * sizeof(bool*));
    for (int i = 0; i < n; i++) {
        g->adj[i] = (bool*)calloc(n, sizeof(bool));
    }
    return g;
}

void graph_free(Graph *g) {
    for (int i = 0; i < g->n; i++) {
        free(g->adj[i]);
    }
    free(g->adj);
    free(g);
}

void graph_add_edge(Graph *g, int u, int v) {
    g->adj[u][v] = true;
    g->adj[v][u] = true;
}

bool check_feasibility(const Graph *g1, const Graph *g2, const int *core1, const int *core2, int u, int v) {
    for (int other1 = 0; other1 < g1->n; other1++) {
        if (g1->adj[u][other1]) {
            int other2 = core1[other1];
            if (other2 != -1) {
                if (!g2->adj[v][other2]) return false;
            }
        }
    }
    for (int other2 = 0; other2 < g2->n; other2++) {
        if (g2->adj[v][other2]) {
            int other1 = core2[other2];
            if (other1 != -1) {
                if (!g1->adj[u][other1]) return false;
            }
        }
    }
    return true;
}

bool match_vf2(const Graph *g1, const Graph *g2, int *core1, int *core2, int depth) {
    if (depth == g1->n) {
        return true;
    }

    int u = -1;
    for (int i = 0; i < g1->n; i++) {
        if (core1[i] == -1) {
            u = i;
            break;
        }
    }

    for (int v = 0; v < g2->n; v++) {
        if (core2[v] == -1) {
            if (check_feasibility(g1, g2, core1, core2, u, v)) {
                core1[u] = v;
                core2[v] = u;

                if (match_vf2(g1, g2, core1, core2, depth + 1)) {
                    return true;
                }

                core1[u] = -1;
                core2[v] = -1;
            }
        }
    }
    return false;
}

bool graph_isomorphism_vf2(const Graph *g1, const Graph *g2, int *mapping) {
    if (g1->n != g2->n) return false;
    int n = g1->n;
    int *core1 = (int*)malloc(n * sizeof(int));
    int *core2 = (int*)malloc(n * sizeof(int));
    for (int i = 0; i < n; i++) {
        core1[i] = -1;
        core2[i] = -1;
    }

    bool result = match_vf2(g1, g2, core1, core2, 0);
    if (result && mapping) {
        for (int i = 0; i < n; i++) mapping[i] = core1[i];
    }

    free(core1);
    free(core2);
    return result;
}

int main(void) {
    Graph *g1 = graph_create(4);
    graph_add_edge(g1, 0, 1);
    graph_add_edge(g1, 1, 2);
    graph_add_edge(g1, 2, 3);
    graph_add_edge(g1, 3, 0);

    Graph *g2 = graph_create(4);
    graph_add_edge(g2, 2, 3);
    graph_add_edge(g2, 3, 0);
    graph_add_edge(g2, 0, 1);
    graph_add_edge(g2, 1, 2);

    int mapping[4];
    if (graph_isomorphism_vf2(g1, g2, mapping)) {
        printf("Графи ізоморфні! Мапінг:\n");
        for (int i = 0; i < 4; i++) {
            printf("  G1[%d] -> G2[%d]\n", i, mapping[i]);
        }
    } else {
        printf("Графи не ізоморфні.\n");
    }

    graph_free(g1);
    graph_free(g2);
    return 0;
}
