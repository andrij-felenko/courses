#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

typedef struct {
    long long* tree;
    long long* lazy;
    size_t n;
} lazy_seg_tree_t;

lazy_seg_tree_t* lazy_segtree_create(size_t n) {
    lazy_seg_tree_t* st = (lazy_seg_tree_t*)malloc(sizeof(lazy_seg_tree_t));
    if (!st) return NULL;

    st->n = n;
    st->tree = (long long*)calloc(4 * n, sizeof(long long));
    st->lazy = (long long*)calloc(4 * n, sizeof(long long));
    if (!st->tree || !st->lazy) {
        free(st->tree);
        free(st->lazy);
        free(st);
        return NULL;
    }
    return st;
}

void lazy_segtree_destroy(lazy_seg_tree_t* st) {
    if (st) {
        free(st->tree);
        free(st->lazy);
        free(st);
    }
}

static void push_down(lazy_seg_tree_t* st, size_t v, size_t tl, size_t tr) {
    if (st->lazy[v] != 0 && tl != tr) {
        size_t tm = tl + (tr - tl) / 2;
        size_t left = 2 * v + 1;
        size_t right = 2 * v + 2;

        st->lazy[left] += st->lazy[v];
        st->tree[left] += st->lazy[v] * (tm - tl + 1);

        st->lazy[right] += st->lazy[v];
        st->tree[right] += st->lazy[v] * (tr - tm);

        st->lazy[v] = 0;
    }
}

void lazy_segtree_update_range(lazy_seg_tree_t* st, size_t v, size_t tl, size_t tr, size_t l, size_t r, long long add_val) {
    if (l > r) return;
    if (l == tl && r == tr) {
        st->tree[v] += add_val * (tr - tl + 1);
        st->lazy[v] += add_val;
        return;
    }
    push_down(st, v, tl, tr);
    size_t tm = tl + (tr - tl) / 2;
    size_t left_r = r < tm ? r : tm;
    size_t right_l = l > tm + 1 ? l : tm + 1;

    if (l <= tm) lazy_segtree_update_range(st, 2 * v + 1, tl, tm, l, left_r, add_val);
    if (r > tm) lazy_segtree_update_range(st, 2 * v + 2, tm + 1, tr, right_l, r, add_val);

    st->tree[v] = st->tree[2 * v + 1] + st->tree[2 * v + 2];
}

long long lazy_segtree_query_range(lazy_seg_tree_t* st, size_t v, size_t tl, size_t tr, size_t l, size_t r) {
    if (l > r) return 0;
    if (l == tl && r == tr) {
        return st->tree[v];
    }
    push_down(st, v, tl, tr);
    size_t tm = tl + (tr - tl) / 2;
    size_t left_r = r < tm ? r : tm;
    size_t right_l = l > tm + 1 ? l : tm + 1;

    long long res_left = 0;
    long long res_right = 0;

    if (l <= tm) res_left = lazy_segtree_query_range(st, 2 * v + 1, tl, tm, l, left_r);
    if (r > tm) res_right = lazy_segtree_query_range(st, 2 * v + 2, tm + 1, tr, right_l, r);

    return res_left + res_right;
}
