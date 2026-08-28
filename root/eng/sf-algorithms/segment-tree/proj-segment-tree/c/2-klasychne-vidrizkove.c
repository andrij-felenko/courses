#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

typedef struct {
    long long* tree;
    size_t n;
} segment_tree_t;

static inline size_t left_child(size_t v) { return 2 * v + 1; }
static inline size_t right_child(size_t v) { return 2 * v + 2; }

segment_tree_t* segtree_create(const long long* arr, size_t n) {
    if (!arr || n == 0) return NULL;

    segment_tree_t* st = (segment_tree_t*)malloc(sizeof(segment_tree_t));
    if (!st) return NULL;

    st->n = n;
    st->tree = (long long*)calloc(4 * n, sizeof(long long));
    if (!st->tree) {
        free(st);
        return NULL;
    }

    void build_impl(size_t v, size_t tl, size_t tr) {
        if (tl == tr) {
            st->tree[v] = arr[tl];
            return;
        }
        size_t tm = tl + (tr - tl) / 2;
        build_impl(left_child(v), tl, tm);
        build_impl(right_child(v), tm + 1, tr);
        st->tree[v] = st->tree[left_child(v)] + st->tree[right_child(v)];
    }

    build_impl(0, 0, n - 1);
    return st;
}

void segtree_destroy(segment_tree_t* st) {
    if (st) {
        free(st->tree);
        free(st);
    }
}

void segtree_update_point(segment_tree_t* st, size_t v, size_t tl, size_t tr, size_t pos, long long new_val) {
    if (tl == tr) {
        st->tree[v] = new_val;
        return;
    }
    size_t tm = tl + (tr - tl) / 2;
    if (pos <= tm) {
        segtree_update_point(st, left_child(v), tl, tm, pos, new_val);
    } else {
        segtree_update_point(st, right_child(v), tm + 1, tr, pos, new_val);
    }
    st->tree[v] = st->tree[left_child(v)] + st->tree[right_child(v)];
}

long long segtree_query_range(const segment_tree_t* st, size_t v, size_t tl, size_t tr, size_t l, size_t r) {
    if (l > r) return 0;
    if (l == tl && r == tr) {
        return st->tree[v];
    }
    size_t tm = tl + (tr - tl) / 2;
    size_t left_r = r < tm ? r : tm;
    size_t right_l = l > tm + 1 ? l : tm + 1;

    long long res_left = 0;
    long long res_right = 0;

    if (l <= tm) {
        res_left = segtree_query_range(st, left_child(v), tl, tm, l, left_r);
    }
    if (r > tm) {
        res_right = segtree_query_range(st, right_child(v), tm + 1, tr, right_l, r);
    }

    return res_left + res_right;
}
