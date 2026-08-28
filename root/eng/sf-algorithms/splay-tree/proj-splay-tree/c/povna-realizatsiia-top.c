#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

typedef struct splay_node {
    int key;
    int value;
    struct splay_node *left;
    struct splay_node *right;
} splay_node_t;

typedef struct splay_tree {
    splay_node_t *root;
    size_t size;
} splay_tree_t;

/* Створення окремого вузла дерева */
splay_node_t *splay_node_create(int key, int value) {
    splay_node_t *node = (splay_node_t *)malloc(sizeof(splay_node_t));
    if (!node) return NULL;
    node->key = key;
    node->value = value;
    node->left = NULL;
    node->right = NULL;
    return node;
}

/*
 * Top-Down Splay: переміщує вузол з ключем key (або найближчий наявний)
 * у корінь дерева root за один прохід зверху вниз.
 */
splay_node_t *splay(splay_node_t *root, int key) {
    if (!root) return NULL;

    splay_node_t dummy;
    dummy.left = dummy.right = NULL;
    splay_node_t *l = &dummy;
    splay_node_t *r = &dummy;

    splay_node_t *t = root;

    while (true) {
        if (key < t->key) {
            if (!t->left) break;
            if (key < t->left->key) {
                /* Обертання Zig-Zig праворуч: обертаємо t навколо t->left */
                splay_node_t *y = t->left;
                t->left = y->right;
                y->right = t;
                t = y;
                if (!t->left) break;
            }
            /* Підвішуємо t до правого піддерева R */
            r->left = t;
            r = t;
            t = t->left;
        } else if (key > t->key) {
            if (!t->right) break;
            if (key > t->right->key) {
                /* Обертання Zig-Zig ліворуч: обертаємо t навколо t->right */
                splay_node_t *y = t->right;
                t->right = y->left;
                y->left = t;
                t = y;
                if (!t->right) break;
            }
            /* Підвішуємо t до лівого піддерева L */
            l->right = t;
            l = t;
            t = t->right;
        } else {
            break; /* Ключ знайдено */
        }
    }

    /* Фінальне збирання: об'єднуємо ліве, праве і центральне піддерева */
    l->right = t->left;
    r->left = t->right;
    t->left = dummy.right;
    t->right = dummy.left;

    return t;
}

/* Створення порожнього дерева */
splay_tree_t *splay_tree_create(void) {
    splay_tree_t *tree = (splay_tree_t *)malloc(sizeof(splay_tree_t));
    if (tree) {
        tree->root = NULL;
        tree->size = 0;
    }
    return tree;
}

/* Вставка пари ключ-значення */
bool splay_tree_insert(splay_tree_t *tree, int key, int value) {
    if (!tree) return false;

    if (!tree->root) {
        tree->root = splay_node_create(key, value);
        if (!tree->root) return false;
        tree->size = 1;
        return true;
    }

    tree->root = splay(tree->root, key);

    if (tree->root->key == key) {
        tree->root->value = value; /* Ключ уже існує — оновлюємо значення */
        return false;
    }

    splay_node_t *new_node = splay_node_create(key, value);
    if (!new_node) return false;

    if (key < tree->root->key) {
        new_node->left = tree->root->left;
        new_node->right = tree->root;
        tree->root->left = NULL;
    } else {
        new_node->right = tree->root->right;
        new_node->left = tree->root;
        tree->root->right = NULL;
    }

    tree->root = new_node;
    tree->size++;
    return true;
}

/* Пошук значення за ключем */
bool splay_tree_find(splay_tree_t *tree, int key, int *out_val) {
    if (!tree || !tree->root) return false;

    tree->root = splay(tree->root, key);
    if (tree->root->key == key) {
        if (out_val) *out_val = tree->root->value;
        return true;
    }
    return false;
}

/* Видалення ключа з дерева */
bool splay_tree_erase(splay_tree_t *tree, int key) {
    if (!tree || !tree->root) return false;

    tree->root = splay(tree->root, key);
    if (tree->root->key != key) return false;

    splay_node_t *to_delete = tree->root;

    if (!tree->root->left) {
        tree->root = tree->root->right;
    } else {
        /*
         * Піднімаємо максимум лівого піддерева в корінь лівого піддерева.
         * Оскільки в ньому немає ключів >= key, новий лівий корінь
         * гарантовано не матиме правого нащадка.
         */
        splay_node_t *left_sub = splay(tree->root->left, key);
        left_sub->right = tree->root->right;
        tree->root = left_sub;
    }

    free(to_delete);
    tree->size--;
    return true;
}

static void free_subtree(splay_node_t *node) {
    if (!node) return;
    free_subtree(node->left);
    free_subtree(node->right);
    free(node);
}

void splay_tree_destroy(splay_tree_t *tree) {
    if (!tree) return;
    free_subtree(tree->root);
    free(tree);
}
