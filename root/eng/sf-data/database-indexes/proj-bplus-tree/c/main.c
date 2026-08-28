#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdint.h>

#define BPLUS_ORDER 4

/* Ідентифікатор кортежу в купі (Tuple ID) */
typedef struct {
    uint32_t page_id;
    uint16_t offset;
} tuple_id_t;

/* Структура вузла B+дерева */
typedef struct bplus_node {
    bool is_leaf;
    int num_keys;
    int64_t keys[BPLUS_ORDER];
    union {
        struct bplus_node* children[BPLUS_ORDER + 1];
        tuple_id_t tids[BPLUS_ORDER];
    };
    struct bplus_node* next; /* Тільки для листів */
    struct bplus_node* parent;
} bplus_node_t;

typedef struct {
    bplus_node_t* root;
} bplus_tree_t;

/* Створення нового вузла */
static bplus_node_t* node_create(bool is_leaf) {
    bplus_node_t* node = (bplus_node_t*)calloc(1, sizeof(bplus_node_t));
    if (!node) return NULL;
    node->is_leaf = is_leaf;
    node->num_keys = 0;
    node->next = NULL;
    node->parent = NULL;
    return node;
}

/* Пошук листового вузла, що містить ключ */
static bplus_node_t* find_leaf(bplus_node_t* root, int64_t key) {
    if (!root) return NULL;
    bplus_node_t* curr = root;
    while (!curr->is_leaf) {
        int i = 0;
        while (i < curr->num_keys && key >= curr->keys[i]) {
            i++;
        }
        curr = curr->children[i];
    }
    return curr;
}

/* Точковий пошук за ключем */
bool bplus_find(bplus_tree_t* tree, int64_t key, tuple_id_t* out_tid) {
    if (!tree || !tree->root) return false;
    bplus_node_t* leaf = find_leaf(tree->root, key);
    for (int i = 0; i < leaf->num_keys; i++) {
        if (leaf->keys[i] == key) {
            if (out_tid) *out_tid = leaf->tids[i];
            return true;
        }
    }
    return false;
}

/* Діапазонне сканування: проходження через ланцюг next */
int bplus_range_scan(bplus_tree_t* tree, int64_t min_key, int64_t max_key,
                     tuple_id_t* results, int max_results) {
    if (!tree || !tree->root) return 0;
    bplus_node_t* leaf = find_leaf(tree->root, min_key);
    int count = 0;

    while (leaf && count < max_results) {
        for (int i = 0; i < leaf->num_keys; i++) {
            if (leaf->keys[i] >= min_key && leaf->keys[i] <= max_key) {
                results[count++] = leaf->tids[i];
                if (count >= max_results) break;
            } else if (leaf->keys[i] > max_key) {
                return count;
            }
        }
        leaf = leaf->next;
    }
    return count;
}

/* Допоміжні функції вставки та розщеплення */
static void insert_into_parent(bplus_tree_t* tree, bplus_node_t* left, int64_t key, bplus_node_t* right);

static void split_leaf(bplus_tree_t* tree, bplus_node_t* leaf, int64_t key, tuple_id_t tid) {
    bplus_node_t* new_leaf = node_create(true);
    int64_t temp_keys[BPLUS_ORDER + 1];
    tuple_id_t temp_tids[BPLUS_ORDER + 1];

    int i = 0, j = 0;
    while (i < leaf->num_keys && leaf->keys[i] < key) {
        temp_keys[j] = leaf->keys[i];
        temp_tids[j] = leaf->tids[i];
        i++; j++;
    }
    temp_keys[j] = key;
    temp_tids[j] = tid;
    j++;
    while (i < leaf->num_keys) {
        temp_keys[j] = leaf->keys[i];
        temp_tids[j] = leaf->tids[i];
        i++; j++;
    }

    int split_idx = (BPLUS_ORDER + 1) / 2;
    leaf->num_keys = split_idx;
    for (i = 0; i < split_idx; i++) {
        leaf->keys[i] = temp_keys[i];
        leaf->tids[i] = temp_tids[i];
    }

    new_leaf->num_keys = (BPLUS_ORDER + 1) - split_idx;
    for (i = 0; i < new_leaf->num_keys; i++) {
        new_leaf->keys[i] = temp_keys[split_idx + i];
        new_leaf->tids[i] = temp_tids[split_idx + i];
    }

    new_leaf->next = leaf->next;
    leaf->next = new_leaf;
    new_leaf->parent = leaf->parent;

    insert_into_parent(tree, leaf, new_leaf->keys[0], new_leaf);
}

static void insert_into_parent(bplus_tree_t* tree, bplus_node_t* left, int64_t key, bplus_node_t* right) {
    bplus_node_t* parent = left->parent;
    if (!parent) {
        /* Створення нового кореня */
        bplus_node_t* new_root = node_create(false);
        new_root->keys[0] = key;
        new_root->children[0] = left;
        new_root->children[1] = right;
        new_root->num_keys = 1;
        left->parent = new_root;
        right->parent = new_root;
        tree->root = new_root;
        return;
    }

    if (parent->num_keys < BPLUS_ORDER) {
        int i = parent->num_keys - 1;
        while (i >= 0 && parent->keys[i] > key) {
            parent->keys[i + 1] = parent->keys[i];
            parent->children[i + 2] = parent->children[i + 1];
            i--;
        }
        parent->keys[i + 1] = key;
        parent->children[i + 2] = right;
        parent->num_keys++;
        right->parent = parent;
    } else {
        /* Розщеплення внутрішнього вузла */
        bplus_node_t* new_parent = node_create(false);
        int64_t temp_keys[BPLUS_ORDER + 1];
        bplus_node_t* temp_children[BPLUS_ORDER + 2];

        int i = 0, j = 0;
        while (i < parent->num_keys && parent->keys[i] < key) {
            temp_keys[j] = parent->keys[i];
            temp_children[j] = parent->children[i];
            i++; j++;
        }
        temp_keys[j] = key;
        temp_children[j] = parent->children[i];
        temp_children[j + 1] = right;
        j++;
        while (i < parent->num_keys) {
            temp_keys[j] = parent->keys[i];
            temp_children[j + 1] = parent->children[i + 1];
            i++; j++;
        }

        int split_idx = (BPLUS_ORDER + 1) / 2;
        int64_t promote_key = temp_keys[split_idx];

        parent->num_keys = split_idx;
        for (i = 0; i < split_idx; i++) {
            parent->keys[i] = temp_keys[i];
            parent->children[i] = temp_children[i];
        }
        parent->children[split_idx] = temp_children[split_idx];

        new_parent->num_keys = BPLUS_ORDER - split_idx;
        for (i = 0; i < new_parent->num_keys; i++) {
            new_parent->keys[i] = temp_keys[split_idx + 1 + i];
            new_parent->children[i] = temp_children[split_idx + 1 + i];
            new_parent->children[i]->parent = new_parent;
        }
        new_parent->children[new_parent->num_keys] = temp_children[BPLUS_ORDER + 1];
        new_parent->children[new_parent->num_keys]->parent = new_parent;

        new_parent->parent = parent->parent;
        insert_into_parent(tree, parent, promote_key, new_parent);
    }
}

/* Вставка запису */
bool bplus_insert(bplus_tree_t* tree, int64_t key, tuple_id_t tid) {
    if (!tree) return false;
    if (!tree->root) {
        tree->root = node_create(true);
        tree->root->keys[0] = key;
        tree->root->tids[0] = tid;
        tree->root->num_keys = 1;
        return true;
    }

    bplus_node_t* leaf = find_leaf(tree->root, key);
    if (leaf->num_keys < BPLUS_ORDER) {
        int i = leaf->num_keys - 1;
        while (i >= 0 && leaf->keys[i] > key) {
            leaf->keys[i + 1] = leaf->keys[i];
            leaf->tids[i + 1] = leaf->tids[i];
            i--;
        }
        leaf->keys[i + 1] = key;
        leaf->tids[i + 1] = tid;
        leaf->num_keys++;
        return true;
    }

    split_leaf(tree, leaf, key, tid);
    return true;
}

/* Звільнення пам'яті */
static void free_node(bplus_node_t* node) {
    if (!node) return;
    if (!node->is_leaf) {
        for (int i = 0; i <= node->num_keys; i++) {
            free_node(node->children[i]);
        }
    }
    free(node);
}

void bplus_destroy(bplus_tree_t* tree) {
    if (tree) {
        free_node(tree->root);
        tree->root = NULL;
    }
}
