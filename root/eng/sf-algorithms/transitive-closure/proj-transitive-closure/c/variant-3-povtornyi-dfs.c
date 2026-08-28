#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

typedef struct node {
    size_t target;
    struct node *next;
} node_t;

typedef struct {
    size_t vertices;
    node_t **adj;
    bool *matrix;
} sparse_tc_t;

sparse_tc_t* sparse_tc_create(size_t v) {
    sparse_tc_t *g = (sparse_tc_t*)malloc(sizeof(sparse_tc_t));
    if (!g) return NULL;
    g->vertices = v;
    g->adj = (node_t**)calloc(v, sizeof(node_t*));
    g->matrix = (bool*)calloc(v * v, sizeof(bool));
    return g;
}

void sparse_tc_add_edge(sparse_tc_t *g, size_t u, size_t v) {
    if (!g || u >= g->vertices || v >= g->vertices) return;
    node_t *new_node = (node_t*)malloc(sizeof(node_t));
    new_node->target = v;
    new_node->next = g->adj[u];
    g->adj[u] = new_node;
}

static void dfs_traverse(sparse_tc_t *g, size_t source, size_t curr) {
    for (node_t *curr_edge = g->adj[curr]; curr_edge != NULL; curr_edge = curr_edge->next) {
        size_t next_v = curr_edge->target;
        if (!g->matrix[source * g->vertices + next_v]) {
            g->matrix[source * g->vertices + next_v] = true;
            dfs_traverse(g, source, next_v);
        }
    }
}

void sparse_tc_compute_dfs(sparse_tc_t *g) {
    if (!g) return;
    for (size_t i = 0; i < g->vertices; ++i) {
        dfs_traverse(g, i, i);
    }
}

void sparse_tc_free(sparse_tc_t *g) {
    if (!g) return;
    for (size_t i = 0; i < g->vertices; ++i) {
        node_t *curr = g->adj[i];
        while (curr) {
            node_t *tmp = curr;
            curr = curr->next;
            free(tmp);
        }
    }
    free(g->adj);
    free(g->matrix);
    free(g);
}
