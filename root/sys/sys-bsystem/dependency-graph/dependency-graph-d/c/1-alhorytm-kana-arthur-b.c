#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

#define MAX_NODES 64

typedef struct {
    int count;
    int edges[MAX_NODES][MAX_NODES];
    int in_degree[MAX_NODES];
} BuildGraph;

void graph_init(BuildGraph* g, int count) {
    g->count = count;
    for (int i = 0; i < count; i++) {
        g->in_degree[i] = 0;
        for (int j = 0; j < count; j++) {
            g->edges[i][j] = 0;
        }
    }
}

void graph_add_edge(BuildGraph* g, int from, int to) {
    g->edges[from][to] = 1;
    g->in_degree[to]++;
}

bool run_kahn_schedule(const BuildGraph* g, int* order_out) {
    int temp_in_degree[MAX_NODES];
    int queue[MAX_NODES];
    int head = 0, tail = 0;
    int processed = 0;

    for (int i = 0; i < g->count; i++) {
        temp_in_degree[i] = g->in_degree[i];
        if (temp_in_degree[i] == 0) {
            queue[tail++] = i;
        }
    }

    while (head < tail) {
        int curr = queue[head++];
        order_out[processed++] = curr;

        for (int next = 0; next < g->count; next++) {
            if (g->edges[curr][next]) {
                temp_in_degree[next]--;
                if (temp_in_degree[next] == 0) {
                    queue[tail++] = next;
                }
            }
        }
    }

    return processed == g->count;
}
