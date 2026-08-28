/*
 * Повна реалізація алгоритму Куна мовою C.
 * Використовує прошитий список суміжності для мінімізації накладних витрат.
 */

#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>

typedef struct {
    int* head;
    int* to;
    int* next;
    int edge_cnt;
    int n, m; // розміри часток U та V
} BipartiteGraph;

BipartiteGraph* graph_create(int n, int m, int max_edges) {
    BipartiteGraph* g = (BipartiteGraph*)malloc(sizeof(BipartiteGraph));
    if (!g) return NULL;
    g->n = n;
    g->m = m;
    g->edge_cnt = 0;
    g->head = (int*)malloc(n * sizeof(int));
    if (!g->head) { free(g); return NULL; }
    memset(g->head, -1, n * sizeof(int));
    g->to = (int*)malloc(max_edges * sizeof(int));
    g->next = (int*)malloc(max_edges * sizeof(int));
    return g;
}

void graph_add_edge(BipartiteGraph* g, int u, int v) {
    if (u < 0 || u >= g->n || v < 0 || v >= g->m) return;
    g->to[g->edge_cnt] = v;
    g->next[g->edge_cnt] = g->head[u];
    g->head[u] = g->edge_cnt++;
}

void graph_free(BipartiteGraph* g) {
    if (!g) return;
    free(g->head);
    free(g->to);
    free(g->next);
    free(g);
}

// Рекурсивний обхід DFS для пошуку доповнюючого шляху
static bool kuhn_dfs(const BipartiteGraph* g, int u, int* used_token, int current_token, int* match) {
    if (used_token[u] == current_token) return false;
    used_token[u] = current_token;

    for (int e = g->head[u]; e != -1; e = g->next[e]) {
        int v = g->to[e];
        if (match[v] == -1 || kuhn_dfs(g, match[v], used_token, current_token, match)) {
            match[v] = u;
            return true;
        }
    }
    return false;
}

// Оптимізований запуск алгоритму Куна з викликом жадібного проходу
int kuhn_max_matching(const BipartiteGraph* g, int* match_out) {
    int* match = (int*)malloc(g->m * sizeof(int));
    int* used_token = (int*)calloc(g->n, sizeof(int));
    for (int i = 0; i < g->m; ++i) match[i] = -1;

    // Попередній жадібний прохід для покриття 70%+ ребер без рекурсії
    int matching_size = 0;
    int* match_u = (int*)malloc(g->n * sizeof(int));
    for (int i = 0; i < g->n; ++i) match_u[i] = -1;

    for (int u = 0; u < g->n; ++u) {
        for (int e = g->head[u]; e != -1; e = g->next[e]) {
            int v = g->to[e];
            if (match[v] == -1) {
                match[v] = u;
                match_u[u] = v;
                matching_size++;
                break;
            }
        }
    }

    // Основний цикл для решти вільних вершин U
    int current_token = 0;
    for (int u = 0; u < g->n; ++u) {
        if (match_u[u] == -1) {
            current_token++;
            if (kuhn_dfs(g, u, used_token, current_token, match)) {
                matching_size++;
            }
        }
    }

    if (match_out) {
        memcpy(match_out, match, g->m * sizeof(int));
    }

    free(match_u);
    free(match);
    free(used_token);
    return matching_size;
}

int main(void) {
    BipartiteGraph* g = graph_create(4, 4, 10);
    graph_add_edge(g, 0, 0);
    graph_add_edge(g, 0, 1);
    graph_add_edge(g, 1, 1);
    graph_add_edge(g, 1, 2);
    graph_add_edge(g, 2, 0);
    graph_add_edge(g, 2, 2);
    graph_add_edge(g, 3, 3);

    int match[4];
    int max_match = kuhn_max_matching(g, match);

    printf("Максимальне паросполучення (C): %d\n", max_match);
    for (int v = 0; v < g->m; ++v) {
        if (match[v] != -1) {
            printf("  v%d <-> u%d\n", v, match[v]);
        }
    }

    graph_free(g);
    return 0;
}
