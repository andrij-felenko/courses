#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

// Вузол двійкового дерева мовою C
typedef struct Node {
    int data;
    struct Node* left;
    struct Node* right;
} Node;

// Створення нового вузла в динамічній пам'яті (купа)
Node* create_node(int value) {
    Node* node = (Node*)malloc(sizeof(Node));
    if (!node) {
        perror("Помилка виділення пам'яті для вузла");
        exit(EXIT_FAILURE);
    }
    node->data = value;
    node->left = NULL;
    node->right = NULL;
    return node;
}

// Звільнення всієї пам'яті дерева (зворотний обхід / Post-order)
void destroy_tree(Node* root) {
    if (root == NULL) return;
    destroy_tree(root->left);
    destroy_tree(root->right);
    free(root);
}
