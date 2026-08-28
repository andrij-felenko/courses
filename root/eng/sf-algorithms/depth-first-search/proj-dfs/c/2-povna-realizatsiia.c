#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

typedef enum {
    WHITE = 0,
    GRAY  = 1,
    BLACK = 2
} Color;

typedef struct Node {
    int target;
    struct Node* next;
} Node;

typedef struct {
    int num_vertices;
    Node** adj;
} Graph;

Graph* graph_create(int vertices) {
    Graph* g = (Graph*)malloc(sizeof(Graph));
    g->num_vertices = vertices;
    g->adj = (Node**)calloc(vertices, sizeof(Node*));
    return g;
}

void graph_add_edge(Graph* g, int u, int v) {
    Node* new_node = (Node*)malloc(sizeof(Node));
    new_node->target = v;
    new_node->next = g->adj[u];
    g->adj[u] = new_node;
}

void graph_destroy(Graph* g) {
    for (int i = 0; i < g->num_vertices; i++) {
        Node* curr = g->adj[i];
        while (curr) {
            Node* tmp = curr;
            curr = curr->next;
            free(tmp);
        }
    }
    free(g->adj);
    free(g);
}

void dfs_visit_recursive(Graph* g, int u, Color* color, int* d, int* f, 
                          int* parent, int* timer, bool* has_cycle) {
    color[u] = GRAY;
    d[u] = ++(*timer);

    for (Node* edge = g->adj[u]; edge != NULL; edge = edge->next) {
        int v = edge->target;

        if (color[v] == WHITE) {
            printf("Ребро (%d -> %d): TREE (ребро дерева)\n", u, v);
            parent[v] = u;
            dfs_visit_recursive(g, v, color, d, f, parent, timer, has_cycle);
        } else if (color[v] == GRAY) {
            printf("Ребро (%d -> %d): BACK (зворотне ребро — виявлено ЦИКЛ!)\n", u, v);
            *has_cycle = true;
        } else {
            if (d[u] < d[v]) {
                printf("Ребро (%d -> %d): FORWARD (пряме ребро)\n", u, v);
            } else {
                printf("Ребро (%d -> %d): CROSS (перехресне ребро)\n", u, v);
            }
        }
    }

    color[u] = BLACK;
    f[u] = ++(*timer);
}

void dfs_recursive_full(Graph* g) {
    int n = g->num_vertices;
    Color* color = (Color*)calloc(n, sizeof(Color));
    int* d = (int*)malloc(n * sizeof(int));
    int* f = (int*)malloc(n * sizeof(int));
    int* parent = (int*)malloc(n * sizeof(int));
    int timer = 0;
    bool has_cycle = false;

    for (int i = 0; i < n; i++) parent[i] = -1;

    printf("=== РЕКУРСИВНИЙ C-DFS ===\n");
    for (int i = 0; i < n; i++) {
        if (color[i] == WHITE) {
            dfs_visit_recursive(g, i, color, d, f, parent, &timer, &has_cycle);
        }
    }

    free(color);
    free(d);
    free(f);
    free(parent);
}
