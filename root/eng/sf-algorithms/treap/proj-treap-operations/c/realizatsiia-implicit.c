#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdint.h>

static uint64_t imp_rng = 12345678901234567ULL;

static uint32_t imp_rand(void) {
    imp_rng ^= imp_rng << 13;
    imp_rng ^= imp_rng >> 7;
    imp_rng ^= imp_rng << 17;
    return (uint32_t)imp_rng;
}

typedef struct ImpNode {
    long long val;
    long long sum;
    int sz;
    bool rev;
    uint32_t priority;
    struct ImpNode *left;
    struct ImpNode *right;
} ImpNode;

static int get_sz(const ImpNode *n) {
    return n ? n->sz : 0;
}

static long long get_sum(const ImpNode *n) {
    return n ? n->sum : 0LL;
}

static void push_up(ImpNode *n) {
    if (!n) return;
    n->sz = 1 + get_sz(n->left) + get_sz(n->right);
    n->sum = n->val + get_sum(n->left) + get_sum(n->right);
}

static void push_down(ImpNode *n) {
    if (!n || !n->rev) return;
    ImpNode *tmp = n->left;
    n->left = n->right;
    n->right = tmp;
    if (n->left) n->left->rev ^= true;
    if (n->right) n->right->rev ^= true;
    n->rev = false;
}

ImpNode* imp_create_node(long long val) {
    ImpNode *n = (ImpNode*)malloc(sizeof(ImpNode));
    if (!n) return NULL;
    n->val = val;
    n->sum = val;
    n->sz = 1;
    n->rev = false;
    n->priority = imp_rand();
    n->left = NULL;
    n->right = NULL;
    return n;
}

/* Розрізання за кількістю елементів:
   L отримує перші k елементів, R отримує решту */
void imp_split(ImpNode *t, int k, ImpNode **l, ImpNode **r) {
    if (!t) {
        *l = NULL;
        *r = NULL;
        return;
    }
    push_down(t);
    int left_sz = get_sz(t->left);
    if (left_sz + 1 <= k) {
        imp_split(t->right, k - left_sz - 1, &(t->right), r);
        *l = t;
    } else {
        imp_split(t->left, k, l, &(t->left));
        *r = t;
    }
    push_up(t);
}

ImpNode* imp_merge(ImpNode *l, ImpNode *r) {
    push_down(l);
    push_down(r);
    if (!l) return r;
    if (!r) return l;
    if (l->priority > r->priority) {
        l->right = imp_merge(l->right, r);
        push_up(l);
        return l;
    } else {
        r->left = imp_merge(l, r->left);
        push_up(r);
        return r;
    }
}

/* Вставка значення val у позицію pos (1-based індексація) */
ImpNode* imp_insert(ImpNode *root, int pos, long long val) {
    ImpNode *l = NULL, *r = NULL;
    imp_split(root, pos - 1, &l, &r);
    ImpNode *m = imp_create_node(val);
    return imp_merge(imp_merge(l, m), r);
}

/* Видалення елемента на позиції pos */
ImpNode* imp_erase(ImpNode *root, int pos) {
    ImpNode *l = NULL, *m = NULL, *r = NULL;
    imp_split(root, pos - 1, &l, &r);
    imp_split(r, 1, &m, &r);
    if (m) free(m);
    return imp_merge(l, r);
}

/* Реверс підвідрізка [l_idx, r_idx] за O(log n) */
ImpNode* imp_reverse(ImpNode *root, int l_idx, int r_idx) {
    ImpNode *l = NULL, *m = NULL, *r = NULL;
    imp_split(root, l_idx - 1, &l, &r);
    imp_split(r, r_idx - l_idx + 1, &m, &r);
    if (m) m->rev ^= true;
    return imp_merge(imp_merge(l, m), r);
}

/* Обчислення суми значень на підвідрізку [l_idx, r_idx] */
long long imp_query_sum(ImpNode **root, int l_idx, int r_idx) {
    ImpNode *l = NULL, *m = NULL, *r = NULL;
    imp_split(*root, l_idx - 1, &l, &r);
    imp_split(r, r_idx - l_idx + 1, &m, &r);
    long long res = get_sum(m);
    *root = imp_merge(imp_merge(l, m), r);
    return res;
}
