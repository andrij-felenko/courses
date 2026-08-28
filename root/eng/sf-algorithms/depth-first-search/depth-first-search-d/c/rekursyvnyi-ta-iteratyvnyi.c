#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

typedef struct {
    int u;
    int neighbor_idx;
} StackFrame;

void dfs_iterative(const Graph* g, int start_node) {
    int n = g->num_vertices;
    Color* color = (Color*)calloc(n, sizeof(Color));
    int* d = (int*)malloc(n * sizeof(int));
    int* f = (int*)malloc(n * sizeof(int));
    int timer = 0;

    StackFrame* stack = (StackFrame*)malloc(n * sizeof(StackFrame));
    int top = -1;

    color[start_node] = GRAY;
    d[start_node] = ++timer;
    stack[++top] = (StackFrame){start_node, 0};

    while (top >= 0) {
        int u = stack[top].u;
        Node* curr = g->adj[u];
        int idx = 0;

        while (curr && idx < stack[top].neighbor_idx) {
            curr = curr->next;
            idx++;
        }

        if (curr != NULL) {
            stack[top].neighbor_idx++;
            int v = curr->target;

            if (color[v] == WHITE) {
                color[v] = GRAY;
                d[v] = ++timer;
                stack[++top] = (StackFrame){v, 0}; // Занурення
            }
        } else {
            color[u] = BLACK;
            f[u] = ++timer;
            top--; // Зняття зі стеку після повного завершення нащадків
        }
    }

    free(color);
    free(d);
    free(f);
    free(stack);
}
