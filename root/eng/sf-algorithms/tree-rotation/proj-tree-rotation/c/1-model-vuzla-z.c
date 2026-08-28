#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <assert.h>

/**
 * @brief Структура вузла двійкового дерева з батьківським вказівником.
 */
typedef struct Node {
    int key;
    int height;
    struct Node *left;
    struct Node *right;
    struct Node *parent;
} Node;

/* Створення нового вузла в динамічній пам'яті */
Node* create_node(int key) {
    Node* node = (Node*)malloc(sizeof(Node));
    if (!node) {
        perror("Не вдалося виділити пам'ять під Node");
        return NULL;
    }
    node->key = key;
    node->height = 1;
    node->left = NULL;
    node->right = NULL;
    node->parent = NULL;
    return node;
}

/* Безпечне зчитування висоти вузла (обробляє NULL) */
int get_height(const Node* node) {
    return node ? node->height : 0;
}

/* Обчислення фактора балансу: height(right) - height(left) */
int get_balance_factor(const Node* node) {
    return node ? get_height(node->right) - get_height(node->left) : 0;
}

/* Оновлення висоти вузла на основі актуальних висот дітей */
void update_height(Node* node) {
    if (node) {
        int lh = get_height(node->left);
        int rh = get_height(node->right);
        node->height = (lh > rh ? lh : rh) + 1;
    }
}
