#include <stdlib.h>
#include <stdbool.h>

typedef struct {
    int* parent;
    int num_vertices;
} PathContextC;

static void c_on_tree_edge_path(int u, int v, void* user_data) {
    PathContextC* ctx = (PathContextC*)user_data;
    ctx->parent[v] = u;
}

int* reconstruct_path_c(const int* parent, int target, int* out_length) {
    if (parent[target] == -1 && target != 0) {
        *out_length = 0;
        return NULL;
    }

    int curr = target;
    int len = 0;
    while (curr != -1) {
        len++;
        curr = parent[curr];
    }

    int* path = (int*)malloc(sizeof(int) * len);
    curr = target;
    for (int i = len - 1; i >= 0; --i) {
        path[i] = curr;
        curr = parent[curr];
    }

    *out_length = len;
    return path;
}
