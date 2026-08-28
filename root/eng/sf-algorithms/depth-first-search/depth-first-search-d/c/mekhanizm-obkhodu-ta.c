#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

typedef enum { WHITE = 0, GRAY = 1, BLACK = 2 } Color;

typedef struct Node {
    int target;
    struct Node* next;
} Node;

typedef struct {
    int num_vertices;
    Node** adj;
} Graph;

void dfs_visit(const Graph* g, int u, Color* color, int* d, int* f, int* timer) {
    color[u] = GRAY;           // 1. Вхід у вершину: позначаємо активною
    d[u] = ++(*timer);         // 2. Фіксуємо час відкриття

    for (Node* edge = g->adj[u]; edge != NULL; edge = edge->next) {
        int v = edge->target;
        if (color[v] == WHITE) { // Якщо сусід білий — занурюємося вглиб
            dfs_visit(g, v, color, d, f, timer);
        }
    }

    color[u] = BLACK;          // 3. Завершення вершини: усі нащадки оброблені
    f[u] = ++(*timer);         // 4. Фіксуємо час завершення
}
