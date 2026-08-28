#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdint.h>
#include <math.h>

typedef struct c_edge_t {
    int to;
    int64_t weight;
    struct c_edge_t* next;
} c_edge_t;

typedef struct {
    size_t n;
    int logn;
    int root;
    bool is_built;

    int* depth;
    int64_t* dist_root;
    int* tin;
    int* tout;
    int timer;

    c_edge_t** head;
    int** up;
} lca_context_t;

lca_context_t* lca_create(size_t num_nodes) {
    lca_context_t* ctx = (lca_context_t*)calloc(1, sizeof(lca_context_t));
    if (!ctx) return NULL;

    ctx->n = num_nodes;
    ctx->logn = (int)ceil(log2(num_nodes + 1)) + 2;
    ctx->is_built = false;

    ctx->depth = (int*)calloc(num_nodes + 1, sizeof(int));
    ctx->dist_root = (int64_t*)calloc(num_nodes + 1, sizeof(int64_t));
    ctx->tin = (int*)calloc(num_nodes + 1, sizeof(int));
    ctx->tout = (int*)calloc(num_nodes + 1, sizeof(int));
    ctx->head = (c_edge_t**)calloc(num_nodes + 1, sizeof(c_edge_t*));

    ctx->up = (int**)malloc((num_nodes + 1) * sizeof(int*));
    for (size_t i = 0; i <= num_nodes; i++) {
        ctx->up[i] = (int*)calloc(ctx->logn, sizeof(int));
    }

    return ctx;
}

int lca_add_edge(lca_context_t* ctx, int u, int v, int64_t weight) {
    if (!ctx || ctx->is_built) return -1;
    if (u < 1 || (size_t)u > ctx->n || v < 1 || (size_t)v > ctx->n) return -2;

    c_edge_t* e1 = (c_edge_t*)malloc(sizeof(c_edge_t));
    e1->to = v; e1->weight = weight; e1->next = ctx->head[u]; ctx->head[u] = e1;

    c_edge_t* e2 = (c_edge_t*)malloc(sizeof(c_edge_t));
    e2->to = u; e2->weight = weight; e2->next = ctx->head[v]; ctx->head[v] = e2;

    return 0;
}

static void c_dfs(lca_context_t* ctx, int u, int p, int d, int64_t w_sum) {
    ctx->tin[u] = ++ctx->timer;
    ctx->depth[u] = d;
    ctx->dist_root[u] = w_sum;
    ctx->up[u][0] = p;

    for (int k = 1; k < ctx->logn; k++) {
        ctx->up[u][k] = ctx->up[ctx->up[u][k - 1]][k - 1];
    }

    for (c_edge_t* e = ctx->head[u]; e != NULL; e = e->next) {
        if (e->to != p) {
            c_dfs(ctx, e->to, u, d + 1, w_sum + e->weight);
        }
    }
    ctx->tout[u] = ++ctx->timer;
}

int lca_build(lca_context_t* ctx, int root) {
    if (!ctx) return -1;
    ctx->root = root;
    ctx->timer = 0;
    c_dfs(ctx, root, root, 0, 0);
    ctx->is_built = true;
    return 0;
}

bool lca_is_ancestor(const lca_context_t* ctx, int u, int v) {
    if (!ctx || !ctx->is_built) return false;
    return ctx->tin[u] <= ctx->tin[v] && ctx->tout[u] >= ctx->tout[v];
}

int lca_query(const lca_context_t* ctx, int u, int v) {
    if (!ctx || !ctx->is_built) return -1;
    if (lca_is_ancestor(ctx, u, v)) return u;
    if (lca_is_ancestor(ctx, v, u)) return v;

    for (int k = ctx->logn - 1; k >= 0; k--) {
        if (!lca_is_ancestor(ctx, ctx->up[u][k], v)) {
            u = ctx->up[u][k];
        }
    }
    return ctx->up[u][0];
}

int lca_kth_ancestor(const lca_context_t* ctx, int u, size_t k) {
    if (!ctx || !ctx->is_built) return -1;
    if ((int)k > ctx->depth[u]) return 0;

    for (int i = 0; i < ctx->logn; i++) {
        if ((k >> i) & 1) {
            u = ctx->up[u][i];
        }
    }
    return u;
}

int64_t lca_weighted_distance(const lca_context_t* ctx, int u, int v) {
    int lca_node = lca_query(ctx, u, v);
    return ctx->dist_root[u] + ctx->dist_root[v] - 2 * ctx->dist_root[lca_node];
}

void lca_destroy(lca_context_t* ctx) {
    if (!ctx) return;
    for (size_t i = 0; i <= ctx->n; i++) {
        c_edge_t* curr = ctx->head[i];
        while (curr) {
            c_edge_t* tmp = curr;
            curr = curr->next;
            free(tmp);
        }
        free(ctx->up[i]);
    }
    free(ctx->up);
    free(ctx->head);
    free(ctx->depth);
    free(ctx->dist_root);
    free(ctx->tin);
    free(ctx->tout);
    free(ctx);
}
