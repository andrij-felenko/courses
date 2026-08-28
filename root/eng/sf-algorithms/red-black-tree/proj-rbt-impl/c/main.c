#include <stdio.h>
#include <stdlib.h>

// Кольори вузлів червоно-чорного дерева
typedef enum { RED, BLACK } NodeColor;

// Структура вузла
typedef struct RBNode {
    int key;
    NodeColor color;
    struct RBNode *left;
    struct RBNode *right;
    struct RBNode *parent;
} RBNode;

// Структура дерева із фіктивним листком nil
typedef struct {
    RBNode *root;
    RBNode *nil;
} RBTree;

// Створення нового червоного вузла
RBNode* create_node(RBTree *tree, int key) {
    RBNode *node = (RBNode*)malloc(sizeof(RBNode));
    if (!node) return NULL;
    node->key = key;
    node->color = RED;
    node->left = tree->nil;
    node->right = tree->nil;
    node->parent = tree->nil;
    return node;
}

// Ініціалізація порожнього дерева
RBTree* rbtree_create(void) {
    RBTree *tree = (RBTree*)malloc(sizeof(RBTree));
    if (!tree) return NULL;
    tree->nil = (RBNode*)malloc(sizeof(RBNode));
    if (!tree->nil) {
        free(tree);
        return NULL;
    }
    tree->nil->color = BLACK;
    tree->nil->left = NULL;
    tree->nil->right = NULL;
    tree->nil->parent = NULL;
    tree->root = tree->nil;
    return tree;
}

// Лівий поворот навколо вузла x
void left_rotate(RBTree *tree, RBNode *x) {
    RBNode *y = x->right;
    x->right = y->left;
    
    if (y->left != tree->nil) {
        y->left->parent = x;
    }
    
    y->parent = x->parent;
    
    if (x->parent == tree->nil) {
        tree->root = y;
    } else if (x == x->parent->left) {
        x->parent->left = y;
    } else {
        x->parent->right = y;
    }
    
    y->left = x;
    x->parent = y;
}

// Правий поворот навколо вузла y
void right_rotate(RBTree *tree, RBNode *y) {
    RBNode *x = y->left;
    y->left = x->right;
    
    if (x->right != tree->nil) {
        x->right->parent = y;
    }
    
    x->parent = y->parent;
    
    if (y->parent == tree->nil) {
        tree->root = x;
    } else if (y == y->parent->right) {
        y->parent->right = x;
    } else {
        y->parent->left = x;
    }
    
    x->right = y;
    y->parent = x;
}

// Відновлення інваріантів після вставки червоного вузла z
void rbtree_insert_fixup(RBTree *tree, RBNode *z) {
    while (z->parent->color == RED) {
        if (z->parent == z->parent->parent->left) {
            RBNode *y = z->parent->parent->right; // Дядько
            if (y->color == RED) { // Випадок 1: Дядько червоний (перефарбування)
                z->parent->color = BLACK;
                y->color = BLACK;
                z->parent->parent->color = RED;
                z = z->parent->parent;
            } else {
                if (z == z->parent->right) { // Випадок 2: Zig-Zag (внутрішній)
                    z = z->parent;
                    left_rotate(tree, z);
                }
                // Випадок 3: Line (зовнішній)
                z->parent->color = BLACK;
                z->parent->parent->color = RED;
                right_rotate(tree, z->parent->parent);
            }
        } else { // Симетрична гілка (батько є правою дитиною)
            RBNode *y = z->parent->parent->left;
            if (y->color == RED) {
                z->parent->color = BLACK;
                y->color = BLACK;
                z->parent->parent->color = RED;
                z = z->parent->parent;
            } else {
                if (z == z->parent->left) {
                    z = z->parent;
                    right_rotate(tree, z);
                }
                z->parent->color = BLACK;
                z->parent->parent->color = RED;
                left_rotate(tree, z->parent->parent);
            }
        }
    }
    tree->root->color = BLACK;
}

// Вставка ключа у дерево
void rbtree_insert(RBTree *tree, int key) {
    RBNode *z = create_node(tree, key);
    if (!z) return;
    RBNode *y = tree->nil;
    RBNode *x = tree->root;
    
    while (x != tree->nil) {
        y = x;
        if (z->key < x->key) {
            x = x->left;
        } else {
            x = x->right;
        }
    }
    
    z->parent = y;
    if (y == tree->nil) {
        tree->root = z;
    } else if (z->key < y->key) {
        y->left = z;
    } else {
        y->right = z;
    }
    
    rbtree_insert_fixup(tree, z);
}

// Рекурсивне вивільнення пам'яті
void free_tree_nodes(RBTree *tree, RBNode *node) {
    if (node != tree->nil) {
        free_tree_nodes(tree, node->left);
        free_tree_nodes(tree, node->right);
        free(node);
    }
}

void rbtree_destroy(RBTree *tree) {
    if (!tree) return;
    free_tree_nodes(tree, tree->root);
    free(tree->nil);
    free(tree);
}

int main(void) {
    RBTree *tree = rbtree_create();
    int keys[] = {10, 20, 30, 15, 25, 5};
    for (int i = 0; i < 6; i++) {
        rbtree_insert(tree, keys[i]);
    }
    printf("Червоно-чорне дерево побудовано. Корінь: %d\n", tree->root->key);
    rbtree_destroy(tree);
    return 0;
}
