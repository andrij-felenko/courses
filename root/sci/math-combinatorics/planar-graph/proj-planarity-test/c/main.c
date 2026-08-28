#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>

#define MAX_VERTICES 100000
#define MAX_EDGES 300000

typedef struct Edge {
    int to;
    int next;
    int id;
} Edge;

typedef struct Graph {
    int num_vertices;
    int num_edges;
    int head[MAX_VERTICES];
    Edge edges[MAX_EDGES * 2];
    int edge_count;
} Graph;

typedef struct DSU {
    int parent[MAX_EDGES * 2];
    int rank[MAX_EDGES * 2];
    int side[MAX_EDGES * 2]; /* 0 - та сама сторона, 1 - протилежна */
} DSU;

void graph_init(Graph* g, int n) {
    g->num_vertices = n;
    g->num_edges = 0;
    g->edge_count = 0;
    for (int i = 0; i < n; ++i) {
        g->head[i] = -1;
    }
}

void graph_add_edge(Graph* g, int u, int v, int id) {
    g->edges[g->edge_count].to = v;
    g->edges[g->edge_count].id = id;
    g->edges[g->edge_count].next = g->head[u];
    g->head[u] = g->edge_count++;

    g->edges[g->edge_count].to = u;
    g->edges[g->edge_count].id = id;
    g->edges[g->edge_count].next = g->head[v];
    g->head[v] = g->edge_count++;
    g->num_edges++;
}

void dsu_init(DSU* d, int n) {
    for (int i = 0; i < n; ++i) {
        d->parent[i] = i;
        d->rank[i] = 0;
        d->side[i] = 0;
    }
}

int dsu_find(DSU* d, int v) {
    if (d->parent[v] == v) return v;
    int root = dsu_find(d, d->parent[v]);
    d->side[v] ^= d->side[d->parent[v]];
    d->parent[v] = root;
    return root;
}

bool dsu_add_conflict(DSU* d, int u, int v) {
    int root_u = dsu_find(d, u);
    int root_v = dsu_find(d, v);

    if (root_u == root_v) {
        /* Якщо у них однакова сторона у поточному розфарбуванні — конфлікт нерозв'язний */
        return (d->side[u] != d->side[v]);
    }

    if (d->rank[root_u] < d->rank[root_v]) {
        int tmp = root_u; root_u = root_v; root_v = tmp;
        tmp = u; u = v; v = tmp;
    }

    d->parent[root_v] = root_u;
    d->side[root_v] = d->side[u] ^ d->side[v] ^ 1;
    if (d->rank[root_u] == d->rank[root_v]) {
        d->rank[root_u]++;
    }
    return true;
}

/* Стан DFS для Left-Right тесту */
typedef struct LRState {
    int height[MAX_VERTICES];
    int low[MAX_VERTICES];
    int low2[MAX_VERTICES];
    int parent_edge[MAX_VERTICES];
    bool visited[MAX_VERTICES];
    int timer;
    DSU dsu;
} LRState;

void lr_dfs1(Graph* g, int u, int p_edge, LRState* st) {
    st->visited[u] = true;
    st->height[u] = ++st->timer;
    st->low[u] = st->height[u];
    st->low2[u] = st->height[u];
    st->parent_edge[u] = p_edge;

    for (int e = g->head[u]; e != -1; e = g->edges[e].next) {
        int v = g->edges[e].to;
        int edge_id = g->edges[e].id;
        if (edge_id == p_edge) continue;

        if (st->visited[v]) {
            /* Зворотне ребро */
            if (st->height[v] < st->low[u]) {
                st->low2[u] = st->low[u];
                st->low[u] = st->height[v];
            } else if (st->height[v] > st->low[u] && st->height[v] < st->low2[u]) {
                st->low2[u] = st->height[v];
            }
        } else {
            /* Деревне ребро */
            lr_dfs1(g, v, edge_id, st);
            if (st->low[v] < st->low[u]) {
                st->low2[u] = (st->low[u] < st->low2[v]) ? st->low[u] : st->low2[v];
                st->low[u] = st->low[v];
            } else if (st->low[v] > st->low[u] && st->low[v] < st->low2[u]) {
                st->low2[u] = st->low[v];
            }
        }
    }
}

bool lr_dfs2(Graph* g, int u, int p_edge, LRState* st) {
    for (int e = g->head[u]; e != -1; e = g->edges[e].next) {
        int v = g->edges[e].to;
        int edge_id = g->edges[e].id;
        if (edge_id == p_edge) continue;

        if (st->height[v] > st->height[u]) {
            /* Прямий обхід деревного ребра */
            if (!lr_dfs2(g, v, edge_id, st)) return false;
        } else if (st->height[v] < st->height[u]) {
            /* Перевірка конфліктів для зворотного ребра */
            if (p_edge != -1 && st->low2[u] >= st->height[v]) {
                if (!dsu_add_conflict(&st->dsu, edge_id, p_edge)) {
                    return false; /* Знайдено топологічний конфлікт (K3,3 або K5) */
                }
            }
        }
    }
    return true;
}

bool is_planar(Graph* g) {
    /* 1. Ейлерове відсікання */
    if (g->num_vertices >= 3 && g->num_edges > 3 * g->num_vertices - 6) {
        return false;
    }
    if (g->num_vertices <= 4) {
        return true;
    }

    LRState st;
    memset(&st, 0, sizeof(LRState));
    dsu_init(&st.dsu, g->num_edges);

    for (int i = 0; i < g->num_vertices; ++i) {
        if (!st.visited[i]) {
            st.timer = 0;
            lr_dfs1(g, i, -1, &st);
            if (!lr_dfs2(g, i, -1, &st)) {
                return false;
            }
        }
    }
    return true;
}

int main(void) {
    Graph g_k5;
    graph_init(&g_k5, 5);
    int e_id = 0;
    for (int i = 0; i < 5; ++i) {
        for (int j = i + 1; j < 5; ++j) {
            graph_add_edge(&g_k5, i, j, e_id++);
        }
    }

    printf("Перевірка K5: %s (очікується: Непланарний)\n",
           is_planar(&g_k5) ? "Планарний" : "Непланарний");

    Graph g_cube;
    graph_init(&g_cube, 8);
    int cube_edges[12][2] = {
        {0,1},{1,2},{2,3},{3,0},
        {4,5},{5,6},{6,7},{7,4},
        {0,4},{1,5},{2,6},{3,7}
    };
    for (int i = 0; i < 12; ++i) {
        graph_add_edge(&g_cube, cube_edges[i][0], cube_edges[i][1], i);
    }

    printf("Перевірка 3D Куба (8 вершин, 12 ребер): %s (очікується: Планарний)\n",
           is_planar(&g_cube) ? "Планарний" : "Непланарний");

    return 0;
}
