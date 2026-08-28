#include <stdbool.h>
#include <stdlib.h>

int bidirectional_bfs_c(int num_vertices, const int* const* adj, const int* adj_sizes, int start, int target) {
    if (start == target) return 0;

    int* dist_f = (int*)malloc(sizeof(int) * num_vertices);
    int* dist_b = (int*)malloc(sizeof(int) * num_vertices);
    for (int i = 0; i < num_vertices; ++i) dist_f[i] = dist_b[i] = -1;

    int* q_f = (int*)malloc(sizeof(int) * num_vertices);
    int* q_b = (int*)malloc(sizeof(int) * num_vertices);
    int head_f = 0, tail_f = 0, head_b = 0, tail_b = 0;

    dist_f[start] = 0; q_f[tail_f++] = start;
    dist_b[target] = 0; q_b[tail_b++] = target;

    int result = -1;

    while (head_f < tail_f && head_b < tail_b) {
        // Крок прямої хвилі
        int u_f = q_f[head_f++];
        for (int i = 0; i < adj_sizes[u_f]; ++i) {
            int v = adj[u_f][i];
            if (dist_b[v] != -1) {
                result = dist_f[u_f] + 1 + dist_b[v];
                goto cleanup;
            }
            if (dist_f[v] == -1) {
                dist_f[v] = dist_f[u_f] + 1;
                q_f[tail_f++] = v;
            }
        }

        // Крок зворотної хвилі
        int u_b = q_b[head_b++];
        for (int i = 0; i < adj_sizes[u_b]; ++i) {
            int v = adj[u_b][i];
            if (dist_f[v] != -1) {
                result = dist_b[u_b] + 1 + dist_f[v];
                goto cleanup;
            }
            if (dist_b[v] == -1) {
                dist_b[v] = dist_b[u_b] + 1;
                q_b[tail_b++] = v;
            }
        }
    }

cleanup:
    free(dist_f); free(dist_b); free(q_f); free(q_b);
    return result;
}
