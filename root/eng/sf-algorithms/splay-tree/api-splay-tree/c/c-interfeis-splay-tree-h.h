#ifndef SPLAY_TREE_H
#define SPLAY_TREE_H

#include <stddef.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

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

/* Створення та знищення */
splay_tree_t *splay_tree_create(void);
void splay_tree_destroy(splay_tree_t *tree);
void splay_tree_clear(splay_tree_t *tree);

/* Пошук та доступ */
bool splay_tree_find(splay_tree_t *tree, int key, int *out_val);
bool splay_tree_contains(splay_tree_t *tree, int key);
bool splay_tree_min(splay_tree_t *tree, int *out_key, int *out_val);
bool splay_tree_max(splay_tree_t *tree, int *out_key, int *out_val);

/* Модифікатори */
bool splay_tree_insert(splay_tree_t *tree, int key, int value);
bool splay_tree_erase(splay_tree_t *tree, int key);

/* Спеціальні структурні операції */
bool splay_tree_split(splay_tree_t *src, int key, splay_tree_t **left_out, splay_tree_t **right_out);
splay_tree_t *splay_tree_join(splay_tree_t *left_tree, splay_tree_t *right_tree);

/* Стан контейнера */
size_t splay_tree_size(const splay_tree_t *tree);
bool splay_tree_empty(const splay_tree_t *tree);

#ifdef __cplusplus
}
#endif

#endif /* SPLAY_TREE_H */
