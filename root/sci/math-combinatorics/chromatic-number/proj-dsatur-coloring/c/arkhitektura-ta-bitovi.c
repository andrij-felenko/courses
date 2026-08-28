#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define MAX_VERTICES 64

typedef struct {
    int num_vertices;
    uint64_t adj[MAX_VERTICES];
} Graph;

typedef struct {
    int colors[MAX_VERTICES];
    int chromatic_number;
    bool is_valid;
    uint64_t iterations;
} ColoringResult;

void graph_init(Graph* g, int num_vertices) {
    if (num_vertices > MAX_VERTICES) num_vertices = MAX_VERTICES;
    g->num_vertices = num_vertices;
    for (int i = 0; i < num_vertices; ++i) {
        g->adj[i] = 0ULL;
    }
}

void graph_add_edge(Graph* g, int u, int v) {
    if (u >= 0 && u < g->num_vertices && v >= 0 && v < g->num_vertices && u != v) {
        g->adj[u] |= (1ULL << v);
        g->adj[v] |= (1ULL << u);
    }
}
