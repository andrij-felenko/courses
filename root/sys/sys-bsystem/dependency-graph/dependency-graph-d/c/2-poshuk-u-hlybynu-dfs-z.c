#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

#define MAX_DFS_NODES 64
#define COLOR_WHITE 0
#define COLOR_GRAY  1
#define COLOR_BLACK 2

typedef struct {
    int count;
    int edges[MAX_DFS_NODES][MAX_DFS_NODES];
    int color[MAX_DFS_NODES];
} DfsGraph;

void dfs_graph_init(DfsGraph* g, int count) {
    g->count = count;
    for (int i = 0; i < count; i++) {
        g->color[i] = COLOR_WHITE;
        for (int j = 0; j < count; j++) {
            g->edges[i][j] = 0;
        }
    }
}

void dfs_add_edge(DfsGraph* g, int from, int to) {
    g->edges[from][to] = 1;
}

static bool dfs_visit(DfsGraph* g, int u, int* order_out, int* order_idx) {
    g->color[u] = COLOR_GRAY;

    for (int v = 0; v < g->count; v++) {
        if (g->edges[u][v]) {
            if (g->color[v] == COLOR_GRAY) {
                return false; // Знайдено back-edge (цикл)
            }
            if (g->color[v] == COLOR_WHITE) {
                if (!dfs_visit(g, v, order_out, order_idx)) {
                    return false;
                }
            }
        }
    }

    g->color[u] = COLOR_BLACK;
    order_out[(*order_idx)++] = u; // Додавання на зворотному ході (post-order)
    return true;
}

bool run_dfs_toposort(DfsGraph* g, int* order_out) {
    int order_idx = 0;
    for (int i = 0; i < g->count; i++) {
        if (g->color[i] == COLOR_WHITE) {
            if (!dfs_visit(g, i, order_out, &order_idx)) {
                return false; // Виявлено цикл
            }
        }
    }
    return true;
}
