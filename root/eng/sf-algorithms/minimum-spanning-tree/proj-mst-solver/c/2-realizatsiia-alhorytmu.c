#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>

typedef struct {
    int u;
    int v;
    int64_t weight;
} RawEdge;

typedef struct {
    int *parent;
    int *rank;
    int count;
} Dsu;

Dsu* dsu_create(int n) {
    Dsu *d = (Dsu*)malloc(sizeof(Dsu));
    if (!d) return NULL;
    d->parent = (int*)malloc(sizeof(int) * n);
    d->rank = (int*)calloc(n, sizeof(int));
    d->count = n;
    for (int i = 0; i < n; ++i) {
        d->parent[i] = i;
    }
    return d;
}

void dsu_free(Dsu *d) {
    if (!d) return;
    free(d->parent);
    free(d->rank);
    free(d);
}

int dsu_find(Dsu *d, int i) {
    if (d->parent[i] == i) return i;
    return d->parent[i] = dsu_find(d, d->parent[i]);
}

bool dsu_union(Dsu *d, int i, int j) {
    int root_i = dsu_find(d, i);
    int root_j = dsu_find(d, j);
    if (root_i == root_j) return false;

    if (d->rank[root_i] < d->rank[root_j]) {
        d->parent[root_i] = root_j;
    } else if (d->rank[root_i] > d->rank[root_j]) {
        d->parent[root_j] = root_i;
    } else {
        d->parent[root_j] = root_i;
        d->rank[root_i]++;
    }
    d->count--;
    return true;
}

MstResult boruvka_mst(int num_vertices, const RawEdge *edges, int num_edges) {
    MstResult res = {0};
    if (num_vertices <= 0) return res;

    res.edges = (MstEdge*)malloc(sizeof(MstEdge) * (num_vertices > 1 ? num_vertices - 1 : 1));
    Dsu *dsu = dsu_create(num_vertices);
    int *cheapest = (int*)malloc(sizeof(int) * num_vertices);

    while (dsu->count > 1) {
        for (int i = 0; i < num_vertices; ++i) {
            cheapest[i] = -1;
        }

        bool progress = false;

        /* Знаходимо найдешевше ребро для кожної компоненти зв'язності */
        for (int i = 0; i < num_edges; ++i) {
            int set_u = dsu_find(dsu, edges[i].u);
            int set_v = dsu_find(dsu, edges[i].v);

            if (set_u == set_v) continue;

            if (cheapest[set_u] == -1 || edges[i].weight < edges[cheapest[set_u]].weight) {
                cheapest[set_u] = i;
            }
            if (cheapest[set_v] == -1 || edges[i].weight < edges[cheapest[set_v]].weight) {
                cheapest[set_v] = i;
            }
        }

        /* Об'єднуємо компоненти за знайденими ребрами */
        for (int i = 0; i < num_vertices; ++i) {
            if (cheapest[i] != -1) {
                int edge_idx = cheapest[i];
                int u = edges[edge_idx].u;
                int v = edges[edge_idx].v;

                if (dsu_union(dsu, u, v)) {
                    res.edges[res.edge_count].u = u;
                    res.edges[res.edge_count].v = v;
                    res.edges[res.edge_count].weight = edges[edge_idx].weight;
                    res.total_weight += edges[edge_idx].weight;
                    res.edge_count++;
                    progress = true;
                }
            }
        }

        if (!progress) break; /* Граф не є зв'язним */
    }

    res.is_connected = (dsu->count == 1);

    dsu_free(dsu);
    free(cheapest);
    return res;
}
