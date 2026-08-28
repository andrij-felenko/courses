#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>

typedef struct {
    size_t vertices;
    bool *matrix; // Плоский масив розміром [V * V]
} graph_tc_t;

graph_tc_t* graph_tc_create(size_t v) {
    if (v == 0) return NULL;
    graph_tc_t *g = (graph_tc_t*)malloc(sizeof(graph_tc_t));
    if (!g) return NULL;
    g->vertices = v;
    g->matrix = (bool*)calloc(v * v, sizeof(bool));
    if (!g->matrix) {
        free(g);
        return NULL;
    }
    return g;
}

void graph_tc_free(graph_tc_t *g) {
    if (!g) return;
    free(g->matrix);
    free(g);
}

void graph_tc_add_edge(graph_tc_t *g, size_t u, size_t v) {
    if (g && u < g->vertices && v < g->vertices) {
        g->matrix[u * g->vertices + v] = true;
    }
}

void graph_tc_compute_warshall(graph_tc_t *g) {
    if (!g || !g->matrix) return;
    const size_t v = g->vertices;
    bool *m = g->matrix;

    for (size_t k = 0; k < v; ++k) {
        for (size_t i = 0; i < v; ++i) {
            if (!m[i * v + k]) continue;
            const size_t i_offset = i * v;
            const size_t k_offset = k * v;
            for (size_t j = 0; j < v; ++j) {
                m[i_offset + j] = m[i_offset + j] || m[k_offset + j];
            }
        }
    }
}

bool graph_tc_is_reachable(const graph_tc_t *g, size_t u, size_t v) {
    if (!g || u >= g->vertices || v >= g->vertices) return false;
    return g->matrix[u * g->vertices + v];
}
