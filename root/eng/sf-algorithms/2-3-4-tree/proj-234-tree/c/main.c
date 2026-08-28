#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

#define MAX_KEYS 3
#define MAX_CHILDREN 4

typedef struct Node234 {
    int num_keys;
    int keys[MAX_KEYS];
    struct Node234* children[MAX_CHILDREN];
} Node234;

typedef struct {
    Node234* root;
} Tree234;

/* Створення нового вузла з нульовими вказівниками */
static Node234* node_create(void) {
    Node234* node = (Node234*)malloc(sizeof(Node234));
    if (!node) return NULL;
    node->num_keys = 0;
    for (int i = 0; i < MAX_CHILDREN; i++) {
        node->children[i] = NULL;
    }
    return node;
}

/* Перевірка, чи є вузол листком */
static bool node_is_leaf(const Node234* node) {
    return node->children[0] == NULL;
}

/* Превентивне розщеплення дочірнього 4-вузла */
static void node_split_child(Node234* parent, int child_idx) {
    Node234* child = parent->children[child_idx];
    Node234* right_sibling = node_create();
    if (!right_sibling) return;

    /* child: [keys[0], keys[1], keys[2]]
       keys[1] піднімається в parent.
       child стає 2-вузлом з keys[0].
       right_sibling стає 2-вузлом з keys[2]. */
    right_sibling->num_keys = 1;
    right_sibling->keys[0] = child->keys[2];

    if (!node_is_leaf(child)) {
        right_sibling->children[0] = child->children[2];
        right_sibling->children[1] = child->children[3];
        child->children[2] = NULL;
        child->children[3] = NULL;
    }

    child->num_keys = 1;

    /* Зсув дочірніх вказівників у батькові вправо */
    for (int i = parent->num_keys; i > child_idx; i--) {
        parent->children[i + 1] = parent->children[i];
    }
    parent->children[child_idx + 1] = right_sibling;

    /* Зсув ключів у батькові вправо */
    for (int i = parent->num_keys - 1; i >= child_idx; i--) {
        parent->keys[i + 1] = parent->keys[i];
    }
    parent->keys[child_idx] = child->keys[1];
    parent->num_keys++;
}

/* Вставка у піддерево за умови, що поточний вузол не є 4-вузлом */
static void node_insert_non_full(Node234* node, int key) {
    int i = node->num_keys - 1;

    if (node_is_leaf(node)) {
        /* Зсув ключів для вставки нового значення у відсортованому порядку */
        while (i >= 0 && key < node->keys[i]) {
            node->keys[i + 1] = node->keys[i];
            i--;
        }
        node->keys[i + 1] = key;
        node->num_keys++;
    } else {
        /* Пошук піддерева для спуску */
        while (i >= 0 && key < node->keys[i]) {
            i--;
        }
        i++;

        /* Якщо дитина на шляху є 4-вузлом — превентивно розщеплюємо її */
        if (node->children[i]->num_keys == MAX_KEYS) {
            node_split_child(node, i);
            if (key > node->keys[i]) {
                i++;
            }
        }
        node_insert_non_full(node->children[i], key);
    }
}

/* Ініціалізація порожнього дерева */
void tree_init(Tree234* tree) {
    tree->root = NULL;
}

/* Вставка ключа у 2-3-4 дерево */
void tree_insert(Tree234* tree, int key) {
    if (tree->root == NULL) {
        tree->root = node_create();
        if (!tree->root) return;
        tree->root->keys[0] = key;
        tree->root->num_keys = 1;
        return;
    }

    /* Якщо корінь заповнений — розщеплюємо його і збільшуємо висоту */
    if (tree->root->num_keys == MAX_KEYS) {
        Node234* new_root = node_create();
        if (!new_root) return;
        new_root->children[0] = tree->root;
        node_split_child(new_root, 0);
        tree->root = new_root;
    }

    node_insert_non_full(tree->root, key);
}

/* Пошук ключа у 2-3-4 дереві */
bool tree_search(const Tree234* tree, int key) {
    Node234* curr = tree->root;
    while (curr != NULL) {
        int i = 0;
        while (i < curr->num_keys && key > curr->keys[i]) {
            i++;
        }
        if (i < curr->num_keys && key == curr->keys[i]) {
            return true;
        }
        if (node_is_leaf(curr)) {
            break;
        }
        curr = curr->children[i];
    }
    return false;
}

/* Рекурсивне звільнення пам'яті вузлів */
static void node_destroy(Node234* node) {
    if (!node) return;
    for (int i = 0; i <= node->num_keys; i++) {
        node_destroy(node->children[i]);
    }
    free(node);
}

/* Знищення дерева */
void tree_destroy(Tree234* tree) {
    node_destroy(tree->root);
    tree->root = NULL;
}

/* Симетричний обхід для друку ключів у зростаючому порядку */
static void node_print_inorder(const Node234* node) {
    if (!node) return;
    for (int i = 0; i < node->num_keys; i++) {
        node_print_inorder(node->children[i]);
        printf("%d ", node->keys[i]);
    }
    node_print_inorder(node->children[node->num_keys]);
}

void tree_print(const Tree234* tree) {
    node_print_inorder(tree->root);
    printf("\n");
}
