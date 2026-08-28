#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

#define MIN(a,b) ((a) < (b) ? (a) : (b))

typedef struct {
    int u;
    EdgeNode* curr_edge;
} FrameC;

void find_scc_iterative_c(const Graph* g) {
    int n = g->num_vertices;
    int* tin = (int*)calloc(n, sizeof(int));
    int* low = (int*)calloc(n, sizeof(int));
    bool* in_stack = (bool*)calloc(n, sizeof(bool));
    int* scc_stack = (int*)malloc(n * sizeof(int));
    int scc_top = -1;
    int timer = 0;

    FrameC* dfs_stack = (FrameC*)malloc(n * sizeof(FrameC));
    int dfs_top = -1;

    for (int start = 0; start < n; start++) {
        if (tin[start] != 0) continue;

        dfs_stack[++dfs_top] = (FrameC){start, g->adj[start]};
        tin[start] = low[start] = ++timer;
        scc_stack[++scc_top] = start;
        in_stack[start] = true;

        while (dfs_top >= 0) {
            FrameC* frame = &dfs_stack[dfs_top];
            int u = frame->u;

            if (frame->curr_edge != NULL) {
                int v = frame->curr_edge->to;
                frame->curr_edge = frame->curr_edge->next;

                if (tin[v] == 0) {
                    tin[v] = low[v] = ++timer;
                    scc_stack[++scc_top] = v;
                    in_stack[v] = true;
                    dfs_stack[++dfs_top] = (FrameC){v, g->adj[v]};
                } else if (in_stack[v]) {
                    low[u] = MIN(low[u], tin[v]);
                }
            } else {
                dfs_top--;
                if (dfs_top >= 0) {
                    int parent = dfs_stack[dfs_top].u;
                    low[parent] = MIN(low[parent], low[u]);
                }

                if (low[u] == tin[u]) {
                    printf("SCC (iterative C): [ ");
                    while (1) {
                        int v = scc_stack[scc_top--];
                        in_stack[v] = false;
                        printf("%d ", v);
                        if (u == v) break;
                    }
                    printf("]\n");
                }
            }
        }
    }

    free(tin); free(low); free(in_stack); free(scc_stack); free(dfs_stack);
}
