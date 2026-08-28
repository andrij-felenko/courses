#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

#define MAXN 100005
#define LOGN 20

typedef struct Edge {
    int to;
    struct Edge* next;
} Edge;

typedef struct {
    Edge* head[MAXN];
    int depth[MAXN];
    int up[MAXN][LOGN];
    int n;
} BinaryLiftingLCA;

BinaryLiftingLCA* lca_create(int n) {
    BinaryLiftingLCA* tree = (BinaryLiftingLCA*)calloc(1, sizeof(BinaryLiftingLCA));
    if (!tree) return NULL;
    tree->n = n;
    return tree;
}

void lca_add_edge(BinaryLiftingLCA* tree, int u, int v) {
    Edge* e1 = (Edge*)malloc(sizeof(Edge));
    e1->to = v; e1->next = tree->head[u]; tree->head[u] = e1;
    
    Edge* e2 = (Edge*)malloc(sizeof(Edge));
    e2->to = u; e2->next = tree->head[v]; tree->head[v] = e2;
}

static void dfs_build(BinaryLiftingLCA* tree, int u, int p, int d) {
    tree->depth[u] = d;
    tree->up[u][0] = p;

    for (int k = 1; k < LOGN; k++) {
        tree->up[u][k] = tree->up[tree->up[u][k - 1]][k - 1];
    }

    for (Edge* e = tree->head[u]; e != NULL; e = e->next) {
        if (e->to != p) {
            dfs_build(tree, e->to, u, d + 1);
        }
    }
}

void lca_init(BinaryLiftingLCA* tree, int root) {
    dfs_build(tree, root, root, 0);
}

int lca_query(const BinaryLiftingLCA* tree, int u, int v) {
    if (tree->depth[u] < tree->depth[v]) {
        int tmp = u; u = v; v = tmp;
    }

    int diff = tree->depth[u] - tree->depth[v];
    for (int k = LOGN - 1; k >= 0; k--) {
        if ((diff >> k) & 1) {
            u = tree->up[u][k];
        }
    }

    if (u == v) return u;

    for (int k = LOGN - 1; k >= 0; k--) {
        if (tree->up[u][k] != tree->up[v][k]) {
            u = tree->up[u][k];
            v = tree->up[v][k];
        }
    }

    return tree->up[u][0];
}

void lca_free(BinaryLiftingLCA* tree) {
    if (!tree) return;
    for (int i = 0; i <= tree->n; i++) {
        Edge* curr = tree->head[i];
        while (curr) {
            Edge* tmp = curr;
            curr = curr->next;
            free(tmp);
        }
    }
    free(tree);
}
