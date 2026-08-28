#include <stdio.h>
#include <stdlib.h>

typedef struct {
    long long* tree;
    size_t n;
} iter_seg_tree_t;

iter_seg_tree_t* iter_segtree_create(const long long* arr, size_t n) {
    iter_seg_tree_t* st = (iter_seg_tree_t*)malloc(sizeof(iter_seg_tree_t));
    if (!st) return NULL;
    st->n = n;
    st->tree = (long long*)malloc(2 * n * sizeof(long long));
    if (!st->tree) {
        free(st);
        return NULL;
    }
    for (size_t i = 0; i < n; i++) {
        st->tree[n + i] = arr[i];
    }
    for (size_t i = n - 1; i > 0; i--) {
        st->tree[i] = st->tree[i << 1] + st->tree[(i << 1) | 1];
    }
    return st;
}

void iter_segtree_update(iter_seg_tree_t* st, size_t pos, long long val) {
    for (st->tree[pos += st->n] = val; pos > 1; pos >>= 1) {
        st->tree[pos >> 1] = st->tree[pos] + st->tree[pos ^ 1];
    }
}

long long iter_segtree_query(const iter_seg_tree_t* st, size_t l, size_t r) {
    long long res = 0;
    for (l += st->n, r += st->n; l < r; l >>= 1, r >>= 1) {
        if (l & 1) res += st->tree[l++];
        if (r & 1) res += st->tree[--r];
    }
    return res;
}

void iter_segtree_destroy(iter_seg_tree_t* st) {
    if (st) {
        free(st->tree);
        free(st);
    }
}
