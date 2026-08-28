#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

typedef struct {
    size_t size;
    long long* tree;
} fenwick_tree_t;

static inline size_t fenwick_lsb(size_t i) {
    return i & (-i);
}

fenwick_tree_t* fenwick_create(size_t size) {
    fenwick_tree_t* ft = (fenwick_tree_t*)malloc(sizeof(fenwick_tree_t));
    if (!ft) return NULL;
    ft->size = size;
    ft->tree = (long long*)calloc(size + 1, sizeof(long long));
    if (!ft->tree) {
        free(ft);
        return NULL;
    }
    return ft;
}

void fenwick_destroy(fenwick_tree_t* ft) {
    if (ft) {
        free(ft->tree);
        free(ft);
    }
}

// Лінійна побудова за O(N)
fenwick_tree_t* fenwick_create_from_array(const long long* data, size_t size) {
    fenwick_tree_t* ft = fenwick_create(size);
    if (!ft) return NULL;

    for (size_t i = 0; i < size; ++i) {
        ft->tree[i + 1] += data[i];
        size_t parent = (i + 1) + fenwick_lsb(i + 1);
        if (parent <= size) {
            ft->tree[parent] += ft->tree[i + 1];
        }
    }
    return ft;
}

bool fenwick_add(fenwick_tree_t* ft, size_t idx, long long val) {
    if (!ft || idx >= ft->size) return false;
    for (size_t i = idx + 1; i <= ft->size; i += fenwick_lsb(i)) {
        ft->tree[i] += val;
    }
    return true;
}

long long fenwick_query_prefix(const fenwick_tree_t* ft, size_t idx) {
    if (!ft || idx >= ft->size) return 0;
    long long sum = 0;
    for (size_t i = idx + 1; i > 0; i -= fenwick_lsb(i)) {
        sum += ft->tree[i];
    }
    return sum;
}

long long fenwick_query_range(const fenwick_tree_t* ft, size_t left, size_t right) {
    if (!ft || left > right || right >= ft->size) return 0;
    if (left == 0) {
        return fenwick_query_prefix(ft, right);
    }
    return fenwick_query_prefix(ft, right) - fenwick_query_prefix(ft, left - 1);
}
