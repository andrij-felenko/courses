#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>

typedef struct {
    int num_vertices;
    bool **adj_matrix;
} graph_t;

graph_t* graph_create(int vertices) {
    graph_t *g = (graph_t*)malloc(sizeof(graph_t));
    if (!g) return NULL;
    g->num_vertices = vertices;
    g->adj_matrix = (bool**)malloc(vertices * sizeof(bool*));
    for (int i = 0; i < vertices; ++i) {
        g->adj_matrix[i] = (bool*)calloc(vertices, sizeof(bool));
    }
    return g;
}

void graph_free(graph_t *g) {
    if (!g) return;
    for (int i = 0; i < g->num_vertices; ++i) {
        free(g->adj_matrix[i]);
    }
    free(g->adj_matrix);
    free(g);
}

void graph_add_edge(graph_t *g, int u, int v) {
    if (u >= 0 && u < g->num_vertices && v >= 0 && v < g->num_vertices) {
        g->adj_matrix[u][v] = true;
        g->adj_matrix[v][u] = true;
    }
}

static bool backtracking_step(const graph_t *g, int curr_v, int count, bool *visited, int *path) {
    if (count == g->num_vertices) {
        int start_v = path[0];
        return g->adj_matrix[curr_v][start_v];
    }

    for (int next_v = 0; next_v < g->num_vertices; ++next_v) {
        if (g->adj_matrix[curr_v][next_v] && !visited[next_v]) {
            visited[next_v] = true;
            path[count] = next_v;

            if (backtracking_step(g, next_v, count + 1, visited, path)) {
                return true;
            }

            visited[next_v] = false;
        }
    }
    return false;
}

bool solve_hamiltonian_backtrack(const graph_t *g, int *out_path) {
    if (!g || g->num_vertices < 3) return false;

    bool *visited = (bool*)calloc(g->num_vertices, sizeof(bool));
    if (!visited) return false;

    visited[0] = true;
    out_path[0] = 0;

    bool found = backtracking_step(g, 0, 1, visited, out_path);
    free(visited);
    return found;
}
