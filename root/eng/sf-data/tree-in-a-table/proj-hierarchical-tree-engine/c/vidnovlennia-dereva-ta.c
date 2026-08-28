#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

#define MAX_NAME_LEN 64
#define MAX_NODES 1024

/* Сирий запис списку суміжності з реляційної таблиці */
typedef struct {
    int id;
    int parent_id; /* 0 означає NULL (корінь) */
    char name[MAX_NAME_LEN];
} FlatRecord;

/* Вузол дерева в оперативній пам'яті */
typedef struct TreeNode {
    int id;
    char name[MAX_NAME_LEN];
    int lft;
    int rgt;
    int depth;
    char path[256];
    struct TreeNode* parent;
    struct TreeNode** children;
    size_t child_count;
    size_t child_capacity;
} TreeNode;

/* Створення нового вузла */
TreeNode* tree_node_create(int id, const char* name) {
    TreeNode* node = (TreeNode*)malloc(sizeof(TreeNode));
    if (!node) return NULL;
    node->id = id;
    strncpy(node->name, name, MAX_NAME_LEN - 1);
    node->name[MAX_NAME_LEN - 1] = '\0';
    node->lft = 0;
    node->rgt = 0;
    node->depth = 0;
    node->path[0] = '\0';
    node->parent = NULL;
    node->child_count = 0;
    node->child_capacity = 4;
    node->children = (TreeNode**)malloc(sizeof(TreeNode*) * node->child_capacity);
    return node;
}

/* Додавання дочірнього вузла з динамічним розширенням масиву */
bool tree_node_add_child(TreeNode* parent, TreeNode* child) {
    if (!parent || !child) return false;
    if (parent->child_count >= parent->child_capacity) {
        size_t new_cap = parent->child_capacity * 2;
        TreeNode** new_arr = (TreeNode**)realloc(parent->children, sizeof(TreeNode*) * new_cap);
        if (!new_arr) return false;
        parent->children = new_arr;
        parent->child_capacity = new_cap;
    }
    parent->children[parent->child_count++] = child;
    child->parent = parent;
    return true;
}

/* Обчислення лівих/правих ключів (Nested Sets) та матеріалізованих шляхів (DFS) */
void tree_compute_metrics(TreeNode* node, int* counter, int current_depth, const char* parent_path) {
    if (!node) return;

    node->lft = (*counter)++;
    node->depth = current_depth;

    if (parent_path && strlen(parent_path) > 0) {
        snprintf(node->path, sizeof(node->path), "%s%d/", parent_path, node->id);
    } else {
        snprintf(node->path, sizeof(node->path), "/%d/", node->id);
    }

    for (size_t i = 0; i < node->child_count; ++i) {
        tree_compute_metrics(node->children[i], counter, current_depth + 1, node->path);
    }

    node->rgt = (*counter)++;
}

/* Виведення ієрархічної структури дерева */
void tree_print(const TreeNode* node) {
    if (!node) return;
    for (int i = 0; i < node->depth; ++i) {
        printf("  ");
    }
    printf("|- [%d] %s (lft: %d, rgt: %d, depth: %d, path: %s)\n",
           node->id, node->name, node->lft, node->rgt, node->depth, node->path);
    for (size_t i = 0; i < node->child_count; ++i) {
        tree_print(node->children[i]);
    }
}

/* Рекурсивне звільнення пам'яті */
void tree_free(TreeNode* node) {
    if (!node) return;
    for (size_t i = 0; i < node->child_count; ++i) {
        tree_free(node->children[i]);
    }
    free(node->children);
    free(node);
}

int main(void) {
    /* Сирі записи списку суміжності, отримані з реляційної таблиці */
    FlatRecord db_records[] = {
        {1, 0, "Каталог"},
        {2, 1, "Електроніка"},
        {3, 1, "Одяг"},
        {4, 2, "Телефони"},
        {5, 2, "Ноутбуки"},
        {6, 3, "Взуття"}
    };
    size_t count = sizeof(db_records) / sizeof(db_records[0]);

    TreeNode* nodes[MAX_NODES] = {0};
    TreeNode* root = NULL;

    /* Фаза 1: Створення об'єктів */
    for (size_t i = 0; i < count; ++i) {
        nodes[db_records[i].id] = tree_node_create(db_records[i].id, db_records[i].name);
    }

    /* Фаза 2: Зв'язування батьків і дітей */
    for (size_t i = 0; i < count; ++i) {
        int id = db_records[i].id;
        int pid = db_records[i].parent_id;
        if (pid == 0) {
            root = nodes[id];
        } else if (nodes[pid] && nodes[id]) {
            tree_node_add_child(nodes[pid], nodes[id]);
        }
    }

    int counter = 1;
    tree_compute_metrics(root, &counter, 0, "");

    printf("Побудоване дерево з обчисленими метриками:\n");
    tree_print(root);

    tree_free(root);
    return 0;
}
