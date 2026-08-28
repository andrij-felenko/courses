#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define MAXN 100005
#define LOGN 20

typedef struct {
    int* euler;
    int* depth;
    int* first;
    int** st;
    int* log_table;
    int tour_len;
    int n;
} FastRMQLCA;

static int min_depth_node(const FastRMQLCA* rmq, int u, int v) {
    return (rmq->depth[u] < rmq->depth[v]) ? u : v;
}

static void dfs_euler(const int* const* adj, const int* deg, int u, int p, int d,
                      FastRMQLCA* rmq, int* visited) {
    rmq->first[u] = rmq->tour_len;
    rmq->euler[rmq->tour_len] = u;
    rmq->depth[rmq->tour_len] = d;
    rmq->tour_len++;

    for (int i = 0; i < deg[u]; i++) {
        int v = adj[u][i];
        if (v != p) {
            dfs_euler(adj, deg, v, u, d + 1, rmq, visited);
            rmq->euler[rmq->tour_len] = u;
            rmq->depth[rmq->tour_len] = d;
            rmq->tour_len++;
        }
    }
}

FastRMQLCA* rmq_lca_create(int n) {
    FastRMQLCA* rmq = (FastRMQLCA*)calloc(1, sizeof(FastRMQLCA));
    rmq->n = n;
    int max_tour = 2 * n + 5;
    rmq->euler = (int*)malloc(sizeof(int) * max_tour);
    rmq->depth = (int*)malloc(sizeof(int) * max_tour);
    rmq->first = (int*)malloc(sizeof(int) * (n + 1));
    rmq->log_table = (int*)malloc(sizeof(int) * max_tour);

    rmq->log_table[1] = 0;
    for (int i = 2; i < max_tour; i++) {
        rmq->log_table[i] = rmq->log_table[i / 2] + 1;
    }

    return rmq;
}

void rmq_lca_build(FastRMQLCA* rmq, const int* const* adj, const int* deg, int root) {
    rmq->tour_len = 0;
    int* visited = (int*)calloc(rmq->n + 1, sizeof(int));
    dfs_euler(adj, deg, root, 0, 0, rmq, visited);
    free(visited);

    int m = rmq->tour_len;
    int log_m = rmq->log_table[m] + 1;

    rmq->st = (int**)malloc(sizeof(int*) * m);
    for (int i = 0; i < m; i++) {
        rmq->st[i] = (int*)malloc(sizeof(int) * log_m);
        rmq->st[i][0] = rmq->euler[i];
    }

    for (int j = 1; j < log_m; j++) {
        for (int i = 0; i + (1 << j) <= m; i++) {
            int node1 = rmq->st[i][j - 1];
            int node2 = rmq->st[i + (1 << (j - 1))][j - 1];
            rmq->st[i][j] = min_depth_node(rmq, node1, node2);
        }
    }
}

int rmq_lca_query(const FastRMQLCA* rmq, int u, int v) {
    int l = rmq->first[u];
    int r = rmq->first[v];
    if (l > r) { int tmp = l; l = r; r = tmp; }

    int len = r - l + 1;
    int k = rmq->log_table[len];

    int node1 = rmq->st[l][k];
    int node2 = rmq->st[r - (1 << k) + 1][k];
    return min_depth_node(rmq, node1, node2);
}

void rmq_lca_free(FastRMQLCA* rmq) {
    if (!rmq) return;
    if (rmq->st) {
        for (int i = 0; i < rmq->tour_len; i++) {
            free(rmq->st[i]);
        }
        free(rmq->st);
    }
    free(rmq->euler);
    free(rmq->depth);
    free(rmq->first);
    free(rmq->log_table);
    free(rmq);
}
