#include <stdio.h>
#include <stdlib.h>

typedef struct pst_node {
    long long val;
    struct pst_node* left;
    struct pst_node* right;
} pst_node_t;

pst_node_t* pst_build(const long long* arr, size_t tl, size_t tr) {
    pst_node_t* node = (pst_node_t*)malloc(sizeof(pst_node_t));
    if (tl == tr) {
        node->val = arr[tl];
        node->left = node->right = NULL;
        return node;
    }
    size_t tm = tl + (tr - tl) / 2;
    node->left = pst_build(arr, tl, tm);
    node->right = pst_build(arr, tm + 1, tr);
    node->val = node->left->val + node->right->val;
    return node;
}

pst_node_t* pst_update(const pst_node_t* prev, size_t tl, size_t tr, size_t pos, long long new_val) {
    pst_node_t* node = (pst_node_t*)malloc(sizeof(pst_node_t));
    if (tl == tr) {
        node->val = new_val;
        node->left = node->right = NULL;
        return node;
    }
    size_t tm = tl + (tr - tl) / 2;
    if (pos <= tm) {
        node->left = pst_update(prev->left, tl, tm, pos, new_val);
        node->right = prev->right;
    } else {
        node->left = prev->left;
        node->right = pst_update(prev->right, tm + 1, tr, pos, new_val);
    }
    node->val = node->left->val + node->right->val;
    return node;
}

long long pst_query(const pst_node_t* node, size_t tl, size_t tr, size_t l, size_t r) {
    if (!node || l > r) return 0;
    if (l == tl && r == tr) return node->val;
    size_t tm = tl + (tr - tl) / 2;
    size_t left_r = r < tm ? r : tm;
    size_t right_l = l > tm + 1 ? l : tm + 1;
    long long res_l = (l <= tm) ? pst_query(node->left, tl, tm, l, left_r) : 0;
    long long res_r = (r > tm) ? pst_query(node->right, tm + 1, tr, right_l, r) : 0;
    return res_l + res_r;
}
