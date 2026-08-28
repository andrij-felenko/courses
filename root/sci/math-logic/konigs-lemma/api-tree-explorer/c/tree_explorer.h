/**
 * @file tree_explorer.h
 * @brief Повний системний інтерфейс C для навігації в локально скінченних нескінченних деревах.
 */

#ifndef TREE_EXPLORER_H
#define TREE_EXPLORER_H

#include <stddef.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    TREE_SUCCESS = 0,
    TREE_ERROR_NULL_POINTER = -1,
    TREE_ERROR_OUT_OF_MEMORY = -2,
    TREE_ERROR_MAX_VISITED_EXCEEDED = -3,
    TREE_ERROR_MAX_DEPTH_EXCEEDED = -4,
    TREE_ERROR_TARGET_NOT_FOUND = -5
} tree_error_t;

typedef enum {
    TREE_STRATEGY_BFS = 0,
    TREE_STRATEGY_IDDFS = 1
} tree_strategy_t;

typedef void* tree_state_t;

typedef size_t (*tree_get_children_fn)(tree_state_t state, 
                                       tree_state_t* out_children, 
                                       size_t max_children, 
                                       void* user_data);

typedef bool (*tree_is_goal_fn)(tree_state_t state, void* user_data);

typedef void (*tree_free_state_fn)(tree_state_t state, void* user_data);

typedef struct {
    tree_strategy_t strategy;
    size_t max_visited_nodes;
    size_t max_depth;
    size_t max_branching_factor;
    void* user_data;
} tree_config_t;

typedef struct tree_explorer tree_explorer_t;

tree_explorer_t* tree_explorer_create(const tree_config_t* config,
                                      tree_get_children_fn get_children,
                                      tree_is_goal_fn is_goal,
                                      tree_free_state_fn free_state);

tree_error_t tree_explorer_search(tree_explorer_t* explorer,
                                  tree_state_t root_state,
                                  tree_state_t* out_found_state);

void tree_explorer_get_stats(const tree_explorer_t* explorer,
                             size_t* out_visited_count,
                             size_t* out_max_depth_reached);

void tree_explorer_destroy(tree_explorer_t* explorer);

#ifdef __cplusplus
}
#endif

#endif /* TREE_EXPLORER_H */
