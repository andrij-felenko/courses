#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

#define MAX_NODES 200005

typedef struct {
    int to;
    int next;
} Edge;

typedef struct {
    int head_edge[MAX_NODES];
    Edge edges[MAX_NODES * 2];
    int edge_cnt;

    int parent[MAX_NODES];
    int depth[MAX_NODES];
    int sz[MAX_NODES];
    int heavy[MAX_NODES];
    int head[MAX_NODES];
    int pos[MAX_NODES];
    int inv_pos[MAX_NODES];
    int cur_pos;

    int64_t initial_val[MAX_NODES];
    int64_t flat_val[MAX_NODES];

    int64_t seg_tree[MAX_NODES * 4];
    int64_t seg_lazy[MAX_NODES * 4];
    int n;
} HLDTree;

static void hld_init(HLDTree *tree, int n) {
    tree->n = n;
    tree->edge_cnt = 0;
    tree->cur_pos = 0;
    memset(tree->head_edge, -1, sizeof(int) * n);
    memset(tree->heavy, -1, sizeof(int) * n);
    memset(tree->seg_lazy, 0, sizeof(int64_t) * (n * 4));
}

static void hld_add_edge(HLDTree *tree, int u, int v) {
    tree->edges[tree->edge_cnt].to = v;
    tree->edges[tree->edge_cnt].next = tree->head_edge[u];
    tree->head_edge[u] = tree->edge_cnt++;

    tree->edges[tree->edge_cnt].to = u;
    tree->edges[tree->edge_cnt].next = tree->head_edge[v];
    tree->head_edge[v] = tree->edge_cnt++;
}

/* Перший прохід DFS: обчислення розмірів піддерев та пошук важких дітей */
static void dfs1(HLDTree *tree, int u, int p, int d) {
    tree->parent[u] = p;
    tree->depth[u] = d;
    tree->sz[u] = 1;
    tree->heavy[u] = -1;
    int max_child_sz = 0;

    for (int e = tree->head_edge[u]; e != -1; e = tree->edges[e].next) {
        int v = tree->edges[e].to;
        if (v == p) continue;
        dfs1(tree, v, u, d + 1);
        tree->sz[u] += tree->sz[v];
        if (tree->sz[v] > max_child_sz) {
            max_child_sz = tree->sz[v];
            tree->heavy[u] = v;
        }
    }
}

/* Другий прохід DFS: нумерація вершин та розбиття на ланцюги */
static void dfs2(HLDTree *tree, int u, int h) {
    tree->head[u] = h;
    tree->pos[u] = tree->cur_pos;
    tree->inv_pos[tree->cur_pos] = u;
    tree->flat_val[tree->cur_pos] = tree->initial_val[u];
    tree->cur_pos++;

    if (tree->heavy[u] != -1) {
        dfs2(tree, tree->heavy[u], h);
    }

    for (int e = tree->head_edge[u]; e != -1; e = tree->edges[e].next) {
        int v = tree->edges[e].to;
        if (v == tree->parent[u] || v == tree->heavy[u]) continue;
        dfs2(tree, v, v);
    }
}

/* Операції дерева відрізків із Lazy Propagation */
static void seg_push(HLDTree *tree, int node, int l, int r) {
    if (tree->seg_lazy[node] == 0) return;
    int64_t lazy = tree->seg_lazy[node];
    int mid = l + (r - l) / 2;

    tree->seg_tree[node * 2 + 1] += lazy * (mid - l + 1);
    tree->seg_lazy[node * 2 + 1] += lazy;

    tree->seg_tree[node * 2 + 2] += lazy * (r - mid);
    tree->seg_lazy[node * 2 + 2] += lazy;

    tree->seg_lazy[node] = 0;
}

static void seg_build(HLDTree *tree, int node, int l, int r) {
    tree->seg_lazy[node] = 0;
    if (l == r) {
        tree->seg_tree[node] = tree->flat_val[l];
        return;
    }
    int mid = l + (r - l) / 2;
    seg_build(tree, node * 2 + 1, l, mid);
    seg_build(tree, node * 2 + 2, mid + 1, r);
    tree->seg_tree[node] = tree->seg_tree[node * 2 + 1] + tree->seg_tree[node * 2 + 2];
}

static void seg_update(HLDTree *tree, int node, int l, int r, int ql, int qr, int64_t val) {
    if (ql <= l && r <= qr) {
        tree->seg_tree[node] += val * (r - l + 1);
        tree->seg_lazy[node] += val;
        return;
    }
    seg_push(tree, node, l, r);
    int mid = l + (r - l) / 2;
    if (ql <= mid) seg_update(tree, node * 2 + 1, l, mid, ql, qr, val);
    if (qr > mid)  seg_update(tree, node * 2 + 2, mid + 1, r, ql, qr, val);
    tree->seg_tree[node] = tree->seg_tree[node * 2 + 1] + tree->seg_tree[node * 2 + 2];
}

static int64_t seg_query(HLDTree *tree, int node, int l, int r, int ql, int qr) {
    if (ql <= l && r <= qr) return tree->seg_tree[node];
    seg_push(tree, node, l, r);
    int mid = l + (r - l) / 2;
    int64_t res = 0;
    if (ql <= mid) res += seg_query(tree, node * 2 + 1, l, mid, ql, qr);
    if (qr > mid)  res += seg_query(tree, node * 2 + 2, mid + 1, r, ql, qr);
    return res;
}

static void hld_build(HLDTree *tree, int root) {
    tree->cur_pos = 0;
    dfs1(tree, root, -1, 0);
    dfs2(tree, root, root);
    seg_build(tree, 0, 0, tree->n - 1);
}

static int hld_lca(HLDTree *tree, int u, int v) {
    while (tree->head[u] != tree->head[v]) {
        if (tree->depth[tree->head[u]] > tree->depth[tree->head[v]]) {
            u = tree->parent[tree->head[u]];
        } else {
            v = tree->parent[tree->head[v]];
        }
    }
    return tree->depth[u] < tree->depth[v] ? u : v;
}

static void hld_update_path(HLDTree *tree, int u, int v, int64_t val) {
    while (tree->head[u] != tree->head[v]) {
        if (tree->depth[tree->head[u]] < tree->depth[tree->head[v]]) {
            int tmp = u; u = v; v = tmp;
        }
        seg_update(tree, 0, 0, tree->n - 1, tree->pos[tree->head[u]], tree->pos[u], val);
        u = tree->parent[tree->head[u]];
    }
    if (tree->depth[u] > tree->depth[v]) {
        int tmp = u; u = v; v = tmp;
    }
    seg_update(tree, 0, 0, tree->n - 1, tree->pos[u], tree->pos[v], val);
}

static int64_t hld_query_path(HLDTree *tree, int u, int v) {
    int64_t sum = 0;
    while (tree->head[u] != tree->head[v]) {
        if (tree->depth[tree->head[u]] < tree->depth[tree->head[v]]) {
            int tmp = u; u = v; v = tmp;
        }
        sum += seg_query(tree, 0, 0, tree->n - 1, tree->pos[tree->head[u]], tree->pos[u]);
        u = tree->parent[tree->head[u]];
    }
    if (tree->depth[u] > tree->depth[v]) {
        int tmp = u; u = v; v = tmp;
    }
    sum += seg_query(tree, 0, 0, tree->n - 1, tree->pos[u], tree->pos[v]);
    return sum;
}

static void hld_update_subtree(HLDTree *tree, int v, int64_t val) {
    seg_update(tree, 0, 0, tree->n - 1, tree->pos[v], tree->pos[v] + tree->sz[v] - 1, val);
}

static int64_t hld_query_subtree(HLDTree *tree, int v) {
    return seg_query(tree, 0, 0, tree->n - 1, tree->pos[v], tree->pos[v] + tree->sz[v] - 1);
}
