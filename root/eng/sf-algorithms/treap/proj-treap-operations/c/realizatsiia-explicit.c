#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdint.h>

/* Швидкий 64-бітний генератор псевдовипадкових чисел Xorshift64 */
static uint64_t rng_state = 88172645463325252ULL;

static uint32_t fast_rand(void) {
    rng_state ^= rng_state << 13;
    rng_state ^= rng_state >> 7;
    rng_state ^= rng_state << 17;
    return (uint32_t)rng_state;
}

typedef struct TreapNode {
    int key;
    uint32_t priority;
    struct TreapNode *left;
    struct TreapNode *right;
} TreapNode;

TreapNode* treap_create_node(int key) {
    TreapNode *node = (TreapNode*)malloc(sizeof(TreapNode));
    if (!node) return NULL;
    node->key = key;
    node->priority = fast_rand();
    node->left = NULL;
    node->right = NULL;
    return node;
}

void treap_destroy(TreapNode *root) {
    if (!root) return;
    treap_destroy(root->left);
    treap_destroy(root->right);
    free(root);
}

/* Розрізання дерева T за ключем k:
   L отримує всі ключі <= k, R отримує всі ключі > k */
void treap_split(TreapNode *t, int k, TreapNode **l, TreapNode **r) {
    if (!t) {
        *l = NULL;
        *r = NULL;
        return;
    }
    if (t->key <= k) {
        treap_split(t->right, k, &(t->right), r);
        *l = t;
    } else {
        treap_split(t->left, k, l, &(t->left));
        *r = t;
    }
}

/* Злиття дерев L та R за умови, що max_key(L) < min_key(R) */
TreapNode* treap_merge(TreapNode *l, TreapNode *r) {
    if (!l) return r;
    if (!r) return l;
    if (l->priority > r->priority) {
        l->right = treap_merge(l->right, r);
        return l;
    } else {
        r->left = treap_merge(l, r->left);
        return r;
    }
}

TreapNode* treap_insert(TreapNode *root, int key) {
    TreapNode *l = NULL, *r = NULL;
    treap_split(root, key, &l, &r);
    TreapNode *m = treap_create_node(key);
    return treap_merge(treap_merge(l, m), r);
}

TreapNode* treap_erase(TreapNode *root, int key) {
    TreapNode *l = NULL, *m = NULL, *r = NULL;
    treap_split(root, key - 1, &l, &r);
    treap_split(r, key, &m, &r);
    if (m) free(m);
    return treap_merge(l, r);
}

bool treap_find(const TreapNode *root, int key) {
    const TreapNode *curr = root;
    while (curr) {
        if (curr->key == key) return true;
        curr = (key < curr->key) ? curr->left : curr->right;
    }
    return false;
}
