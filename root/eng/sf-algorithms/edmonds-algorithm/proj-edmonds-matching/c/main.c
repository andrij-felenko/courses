#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>

#define MAXV 500

typedef struct {
    int head[MAXV];
    int to[MAXV * MAXV];
    int next[MAXV * MAXV];
    int edge_count;
} Graph;

static void graph_init(Graph *g) {
    memset(g->head, -1, sizeof(g->head));
    g->edge_count = 0;
}

static void graph_add_edge(Graph *g, int u, int v) {
    g->to[g->edge_count] = v;
    g->next[g->edge_count] = g->head[u];
    g->head[u] = g->edge_count++;

    g->to[g->edge_count] = u;
    g->next[g->edge_count] = g->head[v];
    g->head[v] = g->edge_count++;
}

/* Глобальні структури стану алгоритму Едмондса */
static int match_arr[MAXV];
static int parent_arr[MAXV];
static int base_arr[MAXV];
static int type_arr[MAXV];  /* -1: невідвідана, 0: парна (Outer), 1: непарна (Inner) */
static int visited_lca[MAXV];
static int queue_arr[MAXV];
static int q_head, q_tail;
static int timer_lca = 0;

static int dsu_find(int u) {
    if (base_arr[u] == u) return u;
    return base_arr[u] = dsu_find(base_arr[u]);
}

static int find_lca(int u, int v) {
    timer_lca++;
    u = dsu_find(u);
    v = dsu_find(v);

    while (true) {
        if (u != -1) {
            if (visited_lca[u] == timer_lca) return u;
            visited_lca[u] = timer_lca;
            if (match_arr[u] != -1) {
                u = dsu_find(parent_arr[match_arr[u]]);
            } else {
                u = -1;
            }
        }
        /* Міняємо місцями u та v для паралельного підйому вгору по дереву */
        int temp = u;
        u = v;
        v = temp;
    }
}

static void mark_blossom(int u, int v, int lca_node) {
    while (dsu_find(u) != lca_node) {
        parent_arr[u] = v;
        v = match_arr[u];

        if (type_arr[v] == 1) {
            type_arr[v] = 0;
            queue_arr[q_tail++] = v;
        }

        base_arr[u] = lca_node;
        base_arr[v] = lca_node;
        u = parent_arr[v];
    }
}

static bool bfs_augment(const Graph *g, int num_vertices, int start_root) {
    for (int i = 0; i < num_vertices; ++i) {
        base_arr[i] = i;
        parent_arr[i] = -1;
        type_arr[i] = -1;
    }

    q_head = 0;
    q_tail = 0;

    type_arr[start_root] = 0;
    queue_arr[q_tail++] = start_root;

    while (q_head < q_tail) {
        int u = queue_arr[q_head++];

        for (int e = g->head[u]; e != -1; e = g->next[e]) {
            int v = g->to[e];

            if (dsu_find(u) == dsu_find(v) || type_arr[v] == 1) {
                continue;
            }

            if (type_arr[v] == -1) {
                parent_arr[v] = u;
                type_arr[v] = 1;

                if (match_arr[v] == -1) {
                    /* Знайдено доповняльний шлях! Оновлюємо паросполучення */
                    int curr = v;
                    while (curr != -1) {
                        int p = parent_arr[curr];
                        int next_p = (p != -1) ? match_arr[p] : -1;
                        match_arr[curr] = p;
                        match_arr[p] = curr;
                        curr = next_p;
                    }
                    return true;
                }

                type_arr[match_arr[v]] = 0;
                queue_arr[q_tail++] = match_arr[v];
            } else if (type_arr[v] == 0) {
                /* Виявлено квітку (ребро між двома парними вершинами) */
                int lca_node = find_lca(u, v);
                mark_blossom(u, v, lca_node);
                mark_blossom(v, u, lca_node);
            }
        }
    }
    return false;
}

int edmonds_max_matching(const Graph *g, int num_vertices) {
    memset(match_arr, -1, sizeof(match_arr));
    memset(visited_lca, 0, sizeof(visited_lca));
    timer_lca = 0;

    int max_matching_size = 0;
    for (int i = 0; i < num_vertices; ++i) {
        if (match_arr[i] == -1) {
            if (bfs_augment(g, num_vertices, i)) {
                max_matching_size++;
            }
        }
    }
    return max_matching_size;
}

int main(void) {
    Graph g;
    graph_init(&g);

    int n = 5;
    /* Граф — непарний цикл 5 вершин (0-1-2-3-4-0) */
    graph_add_edge(&g, 0, 1);
    graph_add_edge(&g, 1, 2);
    graph_add_edge(&g, 2, 3);
    graph_add_edge(&g, 3, 4);
    graph_add_edge(&g, 4, 0);

    int matching_size = edmonds_max_matching(&g, n);
    printf("Розмір найбільшого паросполучення в C5: %d\n", matching_size);

    return 0;
}
