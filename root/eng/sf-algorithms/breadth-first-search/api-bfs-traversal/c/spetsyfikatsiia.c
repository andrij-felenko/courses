#include <stdbool.h>
#include <stdlib.h>

// Контекстна структура відвідувача мовою C
typedef struct BFSVisitorC {
    void* user_data;

    void (*initialize_vertex)(int u, void* user_data);
    void (*start_vertex)(int u, void* user_data);
    void (*discover_vertex)(int u, void* user_data);
    void (*examine_vertex)(int u, void* user_data);
    void (*examine_edge)(int u, int v, void* user_data);
    void (*tree_edge)(int u, int v, void* user_data);
    void (*non_tree_edge)(int u, int v, void* user_data);
    void (*finish_vertex)(int u, void* user_data);
} BFSVisitorC;

// Універсальний рушій BFS мовою C
void c_bfs_run(
    int num_vertices,
    const int* const* adj_lists,
    const int* adj_sizes,
    int start_node,
    const BFSVisitorC* visitor
) {
    bool* visited = (bool*)calloc(num_vertices, sizeof(bool));
    int* queue = (int*)malloc(sizeof(int) * num_vertices);
    int head = 0, tail = 0;

    for (int i = 0; i < num_vertices; ++i) {
        if (visitor->initialize_vertex) {
            visitor->initialize_vertex(i, visitor->user_data);
        }
    }

    if (visitor->start_vertex) {
        visitor->start_vertex(start_node, visitor->user_data);
    }

    visited[start_node] = true;
    if (visitor->discover_vertex) {
        visitor->discover_vertex(start_node, visitor->user_data);
    }
    queue[tail++] = start_node;

    while (head < tail) {
        int u = queue[head++];

        if (visitor->examine_vertex) {
            visitor->examine_vertex(u, visitor->user_data);
        }

        for (int i = 0; i < adj_sizes[u]; ++i) {
            int v = adj_lists[u][i];
            if (visitor->examine_edge) {
                visitor->examine_edge(u, v, visitor->user_data);
            }

            if (!visited[v]) {
                visited[v] = true;
                if (visitor->tree_edge) {
                    visitor->tree_edge(u, v, visitor->user_data);
                }
                if (visitor->discover_vertex) {
                    visitor->discover_vertex(v, visitor->user_data);
                }
                queue[tail++] = v;
            } else {
                if (visitor->non_tree_edge) {
                    visitor->non_tree_edge(u, v, visitor->user_data);
                }
            }
        }

        if (visitor->finish_vertex) {
            visitor->finish_vertex(u, visitor->user_data);
        }
    }

    free(queue);
    free(visited);
}
