#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>

#define MAX_VERTICES 500

typedef struct {
    int num_vertices;
    int num_edges;
    int head[MAX_VERTICES];
    int to[MAX_VERTICES * MAX_VERTICES];
    int next[MAX_VERTICES * MAX_VERTICES];
    int edge_count;
} Graph;

static void graph_init(Graph *g, int n) {
    g->num_vertices = n;
    g->num_edges = 0;
    g->edge_count = 0;
    for (int i = 0; i < n; ++i) {
        g->head[i] = -1;
    }
}

static void graph_add_edge(Graph *g, int u, int v) {
    g->to[g->edge_count] = v;
    g->next[g->edge_count] = g->head[u];
    g->head[u] = g->edge_count++;

    g->to[g->edge_count] = u;
    g->next[g->edge_count] = g->head[v];
    g->head[v] = g->edge_count++;
    g->num_edges++;
}

/* Структура DSU для супервершин квіток */
static int dsu_find(int *base, int u) {
    if (base[u] == u) {
        return u;
    }
    return base[u] = dsu_find(base, base[u]);
}

static void dsu_union(int *base, int u, int v) {
    int root_u = dsu_find(base, u);
    int root_v = dsu_find(base, v);
    if (root_u != root_v) {
        base[root_u] = root_v;
    }
}

/* Знаходження найменшого спільного предка (LCA) у чергувальному лісі */
static int find_lca(const Graph *g, const int *match, int *base, const int *parent, int u, int v) {
    static bool used[MAX_VERTICES];
    memset(used, 0, sizeof(bool) * g->num_vertices);

    while (true) {
        u = dsu_find(base, u);
        used[u] = true;
        if (match[u] == -1) {
            break;
        }
        u = parent[match[u]];
    }

    while (true) {
        v = dsu_find(base, v);
        if (used[v]) {
            return v;
        }
        if (match[v] == -1) {
            break;
        }
        v = parent[match[v]];
    }

    return -1;
}

/* Стягування квітки вздовж одного рукава */
static void contract_blossom_arm(int *queue, int *tail, const int *match, int *base,
                                 int *parent, bool *in_queue, int u, int v, int lca) {
    while (dsu_find(base, u) != lca) {
        parent[u] = v;
        v = match[u];
        if (!in_queue[v]) {
            in_queue[v] = true;
            queue[(*tail)++] = v;
        }
        dsu_union(base, u, lca);
        dsu_union(base, v, lca);
        u = parent[v];
    }
}

/* Пошук доповняльного шляху методом BFS */
static int find_augmenting_path(const Graph *g, int *match, int *parent, int *base, int root) {
    static int queue[MAX_VERTICES];
    static bool in_queue[MAX_VERTICES];
    static bool in_tree[MAX_VERTICES];

    int head = 0;
    int tail = 0;

    for (int i = 0; i < g->num_vertices; ++i) {
        base[i] = i;
        parent[i] = -1;
        in_queue[i] = false;
        in_tree[i] = false;
    }

    queue[tail++] = root;
    in_queue[root] = true;
    in_tree[root] = true;

    while (head < tail) {
        int u = queue[head++];
        in_queue[u] = false;

        for (int e = g->head[u]; e != -1; e = g->next[e]) {
            int v = g->to[e];

            if (dsu_find(base, u) == dsu_find(base, v) || match[u] == v) {
                continue;
            }

            if (v == root || (match[v] != -1 && parent[match[v]] != -1)) {
                /* Знайдено квітку: ребро між двома S-вершинами */
                int lca = find_lca(g, match, base, parent, u, v);
                if (lca != -1) {
                    contract_blossom_arm(queue, &tail, match, base, parent, in_queue, u, v, lca);
                    contract_blossom_arm(queue, &tail, match, base, parent, in_queue, v, u, lca);
                }
            } else if (parent[v] == -1) {
                parent[v] = u;
                if (match[v] == -1) {
                    /* Знайдено вільну вершину — кінець доповняльного шляху */
                    return v;
                }
                int w = match[v];
                parent[w] = v;
                if (!in_queue[w]) {
                    in_queue[w] = true;
                    queue[tail++] = w;
                }
            }
        }
    }

    return -1;
}

/* Головна функція знаходження максимального паросполучення Едмондса */
int edmonds_max_matching(const Graph *g, int *match) {
    int parent[MAX_VERTICES];
    int base[MAX_VERTICES];
    int matching_size = 0;

    for (int i = 0; i < g->num_vertices; ++i) {
        match[i] = -1;
    }

    for (int i = 0; i < g->num_vertices; ++i) {
        if (match[i] != -1) {
            continue;
        }

        int target = find_augmenting_path(g, match, parent, base, i);
        if (target != -1) {
            /* Аугментація паросполучення вздовж знайденого шляху */
            int curr = target;
            while (curr != -1) {
                int p = parent[curr];
                int next_node = (p != -1) ? match[p] : -1;
                match[curr] = p;
                if (p != -1) {
                    match[p] = curr;
                }
                curr = next_node;
            }
            matching_size++;
        }
    }

    return matching_size;
}
