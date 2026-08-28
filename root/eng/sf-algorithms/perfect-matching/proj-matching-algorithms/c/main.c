#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>

#define MAX_VERTICES 500

typedef struct {
    int num_vertices;
    int adj[MAX_VERTICES][MAX_VERTICES];
    int deg[MAX_VERTICES];
} Graph;

static int match_arr[MAX_VERTICES];
static int parent_arr[MAX_VERTICES];
static int base_arr[MAX_VERTICES];
static int state_arr[MAX_VERTICES]; // -1: unvisited, 0: even, 1: odd
static bool in_blossom[MAX_VERTICES];

static int queue[MAX_VERTICES];
static int q_head = 0, q_tail = 0;

void graph_init(Graph* g, int n) {
    g->num_vertices = n;
    for (int i = 0; i < n; ++i) {
        g->deg[i] = 0;
    }
}

void graph_add_edge(Graph* g, int u, int v) {
    g->adj[u][g->deg[u]++] = v;
    g->adj[v][g->deg[v]++] = u;
}

static int lca(int u, int v) {
    static bool in_path[MAX_VERTICES];
    memset(in_path, 0, sizeof(in_path));

    while (1) {
        u = base_arr[u];
        in_path[u] = true;
        if (match_arr[u] == -1) break;
        u = parent_arr[match_arr[u]];
    }

    while (1) {
        v = base_arr[v];
        if (in_path[v]) return v;
        v = parent_arr[match_arr[v]];
    }
}

static void mark_blossom(int u, int v, int b) {
    while (base_arr[u] != b) {
        in_blossom[base_arr[u]] = true;
        in_blossom[base_arr[v]] = true;
        parent_arr[u] = v;
        v = match_arr[u];
        u = parent_arr[v];
    }
}

static int find_augmenting_path(Graph* g, int root) {
    for (int i = 0; i < g->num_vertices; ++i) {
        state_arr[i] = -1;
        base_arr[i] = i;
        parent_arr[i] = -1;
    }

    q_head = q_tail = 0;
    queue[q_tail++] = root;
    state_arr[root] = 0;

    while (q_head < q_tail) {
        int u = queue[q_head++];

        for (int i = 0; i < g->deg[u]; ++i) {
            int v = g->adj[u][i];

            if (base_arr[u] == base_arr[v] || match_arr[u] == v) continue;

            if (state_arr[v] == -1) {
                parent_arr[v] = u;
                state_arr[v] = 1;

                if (match_arr[v] == -1) {
                    return v; // Доповнювальний шлях знайдено
                }

                int w = match_arr[v];
                state_arr[w] = 0;
                parent_arr[w] = v;
                queue[q_tail++] = w;
            } else if (state_arr[base_arr[v]] == 0) {
                // Виявлено непарний цикл (blossom)
                int b = lca(u, v);
                memset(in_blossom, 0, sizeof(in_blossom));

                mark_blossom(u, v, b);
                mark_blossom(v, u, b);

                for (int i_v = 0; i_v < g->num_vertices; ++i_v) {
                    if (in_blossom[base_arr[i_v]]) {
                        base_arr[i_v] = b;
                        if (state_arr[i_v] == 1) {
                            state_arr[i_v] = 0;
                            queue[q_tail++] = i_v;
                        }
                    }
                }
            }
        }
    }
    return -1;
}

int edmonds_max_matching(Graph* g) {
    for (int i = 0; i < g->num_vertices; ++i) match_arr[i] = -1;

    int matching_size = 0;
    for (int i = 0; i < g->num_vertices; ++i) {
        if (match_arr[i] == -1) {
            int v = find_augmenting_path(g, i);
            if (v != -1) {
                // Доповнення паросполучення уздовж знайденого шляху
                while (v != -1) {
                    int pv = parent_arr[v];
                    int ppv = match_arr[pv];
                    match_arr[v] = pv;
                    match_arr[pv] = v;
                    v = ppv;
                }
                matching_size++;
            }
        }
    }
    return matching_size;
}

bool is_perfect_matching(Graph* g) {
    if (g->num_vertices % 2 != 0) return false;
    return edmonds_max_matching(g) == (g->num_vertices / 2);
}
