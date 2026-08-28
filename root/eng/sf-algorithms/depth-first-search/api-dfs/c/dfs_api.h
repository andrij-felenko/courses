// C API (dfs_api.h) — реалізація на вказівниках на функції
#ifndef DFS_API_H
#define DFS_API_H

#include <stddef.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
    int num_vertices;
    int** adj_matrix;
} dfs_graph_t;

typedef struct {
    void (*initialize_vertex)(int u, void* user_data);
    void (*start_vertex)(int u, void* user_data);
    void (*discover_vertex)(int u, int discovery_time, void* user_data);
    void (*examine_edge)(int u, int v, void* user_data);
    void (*tree_edge)(int u, int v, void* user_data);
    void (*back_edge)(int u, int v, void* user_data);
    void (*forward_or_cross_edge)(int u, int v, void* user_data);
    void (*finish_edge)(int u, int v, void* user_data);
    void (*finish_vertex)(int u, int finish_time, void* user_data);
} dfs_visitor_t;

typedef struct {
    bool stop_on_cycle;
    bool process_all_components;
} dfs_config_t;

bool dfs_traverse(const dfs_graph_t* graph, 
                  const dfs_visitor_t* visitor, 
                  void* user_data, 
                  const dfs_config_t* config);

#ifdef __cplusplus
}
#endif

#endif // DFS_API_H
