#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

#define T 3  /* Мінімальний ступінь B-дерева (t = 3) */
#define MAX_KEYS (2 * T - 1)  /* 5 ключів */
#define MAX_CHILDREN (2 * T)  /* 6 дітей */

typedef struct BTreeNode {
    int keys[MAX_KEYS];
    struct BTreeNode* children[MAX_CHILDREN];
    int num_keys;
    bool is_leaf;
} BTreeNode;

typedef struct BTree {
    BTreeNode* root;
} BTree;

/* Створення нового вузла B-дерева */
BTreeNode* create_node(bool is_leaf) {
    BTreeNode* node = (BTreeNode*)malloc(sizeof(BTreeNode));
    if (!node) {
        perror("Помилка виділення пам'яті для вузла");
        exit(EXIT_FAILURE);
    }
    node->num_keys = 0;
    node->is_leaf = is_leaf;
    for (int i = 0; i < MAX_CHILDREN; i++) {
        node->children[i] = NULL;
    }
    return node;
}

/* Створення порожнього B-дерева */
BTree* create_btree(void) {
    BTree* tree = (BTree*)malloc(sizeof(BTree));
    if (!tree) {
        perror("Помилка виділення пам'яті для дерева");
        exit(EXIT_FAILURE);
    }
    tree->root = create_node(true);
    return tree;
}

/* Пошук ключа у піддереві */
BTreeNode* btree_search(BTreeNode* node, int key, int* out_index) {
    int i = 0;
    while (i < node->num_keys && key > node->keys[i]) {
        i++;
    }
    if (i < node->num_keys && key == node->keys[i]) {
        if (out_index) *out_index = i;
        return node;
    }
    if (node->is_leaf) {
        return NULL;
    }
    return btree_search(node->children[i], key, out_index);
}

/* Розщеплення повного дочірнього вузла parent->children[i] */
void btree_split_child(BTreeNode* parent, int i, BTreeNode* full_child) {
    /* Створюємо новий вузол, який отримає (T - 1) ключів від full_child */
    BTreeNode* new_child = create_node(full_child->is_leaf);
    new_child->num_keys = T - 1;

    /* Копіюємо останні (T - 1) ключів з full_child у new_child */
    for (int j = 0; j < T - 1; j++) {
        new_child->keys[j] = full_child->keys[j + T];
    }

    /* Якщо full_child не є листком, копіюємо також дочірні вказівники */
    if (!full_child->is_leaf) {
        for (int j = 0; j < T; j++) {
            new_child->children[j] = full_child->children[j + T];
        }
    }

    /* Зменшуємо кількість ключів у full_child */
    full_child->num_keys = T - 1;

    /* Зсуваємо дітей у parent, щоб звільнити місце для new_child */
    for (int j = parent->num_keys; j >= i + 1; j--) {
        parent->children[j + 1] = parent->children[j];
    }
    parent->children[i + 1] = new_child;

    /* Зсуваємо ключі у parent, щоб підняти медіанний ключ з full_child */
    for (int j = parent->num_keys - 1; j >= i; j--) {
        parent->keys[j + 1] = parent->keys[j];
    }
    parent->keys[i] = full_child->keys[T - 1];
    parent->num_keys++;
}

/* Додавання ключа у неповний вузол */
void btree_insert_non_full(BTreeNode* node, int key) {
    int i = node->num_keys - 1;

    if (node->is_leaf) {
        /* Шукаємо позицію та зсуваємо ключі праворуч */
        while (i >= 0 && node->keys[i] > key) {
            node->keys[i + 1] = node->keys[i];
            i--;
        }
        node->keys[i + 1] = key;
        node->num_keys++;
    } else {
        /* Знаходимо піддерево для спуску */
        while (i >= 0 && node->keys[i] > key) {
            i--;
        }
        i++;
        /* Якщо дочірній вузол повний — розщеплюємо його превентивно */
        if (node->children[i]->num_keys == MAX_KEYS) {
            btree_split_child(node, i, node->children[i]);
            if (key > node->keys[i]) {
                i++;
            }
        }
        btree_insert_non_full(node->children[i], key);
    }
}

/* Головна функція вставки */
void btree_insert(BTree* tree, int key) {
    BTreeNode* root = tree->root;
    if (root->num_keys == MAX_KEYS) {
        /* Корінь повний: створюємо новий корінь і розщеплюємо старий */
        BTreeNode* new_root = create_node(false);
        tree->root = new_root;
        new_root->children[0] = root;
        btree_split_child(new_root, 0, root);
        btree_insert_non_full(new_root, key);
    } else {
        btree_insert_non_full(root, key);
    }
}

/* Симетричний обхід (In-order traversal) */
void btree_traverse(BTreeNode* node) {
    if (!node) return;
    int i;
    for (i = 0; i < node->num_keys; i++) {
        if (!node->is_leaf) {
            btree_traverse(node->children[i]);
        }
        printf("%d ", node->keys[i]);
    }
    if (!node->is_leaf) {
        btree_traverse(node->children[i]);
    }
}

/* Рекурсивне звільнення пам'яті */
void free_node(BTreeNode* node) {
    if (!node) return;
    if (!node->is_leaf) {
        for (int i = 0; i <= node->num_keys; i++) {
            free_node(node->children[i]);
        }
    }
    free(node);
}

void free_btree(BTree* tree) {
    if (!tree) return;
    free_node(tree->root);
    free(tree);
}

int main(void) {
    BTree* tree = create_btree();
    int keys[] = {10, 20, 5, 6, 12, 30, 7, 17, 3, 22, 27, 45, 1, 35};
    int n = sizeof(keys) / sizeof(keys[0]);

    for (int i = 0; i < n; i++) {
        btree_insert(tree, keys[i]);
    }

    printf("Обхід B-дерева у порядку зростання:\n");
    btree_traverse(tree->root);
    printf("\n");

    int search_key = 17;
    int idx;
    BTreeNode* found = btree_search(tree->root, search_key, &idx);
    if (found) {
        printf("Ключ %d знайдено у вузлі на позиції %d\n", search_key, idx);
    } else {
        printf("Ключ %d не знайдено\n", search_key);
    }

    free_btree(tree);
    return 0;
}
