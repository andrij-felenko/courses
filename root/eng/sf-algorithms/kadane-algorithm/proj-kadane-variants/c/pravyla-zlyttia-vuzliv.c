#include <stdio.h>
#include <stdlib.h>

typedef struct {
    long long total_sum;
    long long max_prefix;
    long long max_suffix;
    long long max_subarray;
} SegmentNode;

static inline long long max2(long long a, long long b) {
    return (a > b) ? a : b;
}

static inline long long max3(long long a, long long b, long long c) {
    return max2(a, max2(b, c));
}

SegmentNode make_leaf(long long val) {
    SegmentNode node;
    node.total_sum = val;
    node.max_prefix = val;
    node.max_suffix = val;
    node.max_subarray = val;
    return node;
}

SegmentNode merge_nodes(SegmentNode L, SegmentNode R) {
    SegmentNode res;
    res.total_sum = L.total_sum + R.total_sum;
    res.max_prefix = max2(L.max_prefix, L.total_sum + R.max_prefix);
    res.max_suffix = max2(R.max_suffix, R.total_sum + L.max_suffix);
    res.max_subarray = max3(L.max_subarray, R.max_subarray, L.max_suffix + R.max_prefix);
    return res;
}

void build_tree(const int* arr, SegmentNode* tree, int v, int tl, int tr) {
    if (tl == tr) {
        tree[v] = make_leaf(arr[tl]);
        return;
    }
    int tm = (tl + tr) / 2;
    build_tree(arr, tree, 2 * v, tl, tm);
    build_tree(arr, tree, 2 * v + 1, tm + 1, tr);
    tree[v] = merge_nodes(tree[2 * v], tree[2 * v + 1]);
}

void update_tree(SegmentNode* tree, int v, int tl, int tr, int pos, long long new_val) {
    if (tl == tr) {
        tree[v] = make_leaf(new_val);
        return;
    }
    int tm = (tl + tr) / 2;
    if (pos <= tm) {
        update_tree(tree, 2 * v, tl, tm, pos, new_val);
    } else {
        update_tree(tree, 2 * v + 1, tm + 1, tr, pos, new_val);
    }
    tree[v] = merge_nodes(tree[2 * v], tree[2 * v + 1]);
}

SegmentNode query_tree(const SegmentNode* tree, int v, int tl, int tr, int l, int r) {
    if (l <= tl && tr <= r) {
        return tree[v];
    }
    int tm = (tl + tr) / 2;
    if (r <= tm) {
        return query_tree(tree, 2 * v, tl, tm, l, r);
    }
    if (l > tm) {
        return query_tree(tree, 2 * v + 1, tm + 1, tr, l, r);
    }
    SegmentNode left_res = query_tree(tree, 2 * v, tl, tm, l, r);
    SegmentNode right_res = query_tree(tree, 2 * v + 1, tm + 1, tr, l, r);
    return merge_nodes(left_res, right_res);
}
