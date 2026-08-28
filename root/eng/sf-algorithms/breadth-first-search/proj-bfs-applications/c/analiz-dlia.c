#include <stdbool.h>
#include <stdlib.h>

bool is_bipartite_c(int num_vertices, const int* const* adj, const int* adj_sizes) {
    int* color = (int*)calloc(num_vertices, sizeof(int));
    int* queue = (int*)malloc(sizeof(int) * num_vertices);

    for (int start = 0; start < num_vertices; ++start) {
        if (color[start] != 0) continue;

        int head = 0, tail = 0;
        color[start] = 1;
        queue[tail++] = start;

        while (head < tail) {
            int u = queue[head++];
            for (int i = 0; i < adj_sizes[u]; ++i) {
                int v = adj[u][i];
                if (color[v] == 0) {
                    color[v] = 3 - color[u];
                    queue[tail++] = v;
                } else if (color[v] == color[u]) {
                    free(color); free(queue);
                    return false;
                }
            }
        }
    }
    free(color); free(queue);
    return true;
}
