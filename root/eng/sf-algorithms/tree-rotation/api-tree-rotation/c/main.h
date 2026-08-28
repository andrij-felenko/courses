#ifndef TREE_ROTATION_H
#define TREE_ROTATION_H

#include <stddef.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Структура вузла двійкового дерева з розширеними метаданими.
 */
typedef struct Node {
    int key;                /**< Ключ вузла для порівняння */
    int height;             /**< Висота піддерева з коренем у даному вузлі */
    size_t size;            /**< Кількість вузлів у піддереві (для порядкових статистик) */
    struct Node *left;      /**< Вказівник на лівого сина */
    struct Node *right;     /**< Вказівник на правого сина */
    struct Node *parent;    /**< Вказівник на батьківський вузол */
} Node;

Node* rotate_right(Node* x, Node** root);
Node* rotate_left(Node* x, Node** root);
Node* rotate_left_right(Node* z, Node** root);
Node* rotate_right_left(Node* z, Node** root);
bool validate_tree_invariants(const Node* node);

#ifdef __cplusplus
}
#endif

#endif /* TREE_ROTATION_H */
