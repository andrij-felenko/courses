#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

bool solve_hamiltonian_held_karp(const graph_t *g, int *out_path) {
    int n = g->num_vertices;
    if (n < 3 || n > 31) return false;

    int num_states = 1 << n;
    bool **dp = (bool**)malloc(num_states * sizeof(bool*));
    int **parent = (int**)malloc(num_states * sizeof(int*));
    for (int i = 0; i < num_states; ++i) {
        dp[i] = (bool*)calloc(n, sizeof(bool));
        parent[i] = (int*)malloc(n * sizeof(int));
        for (int j = 0; j < n; ++j) parent[i][j] = -1;
    }

    dp[1][0] = true;

    for (int mask = 1; mask < num_states; ++mask) {
        if (!(mask & 1)) continue;

        for (int v = 0; v < n; ++v) {
            if (!(mask & (1 << v)) || !dp[mask][v]) continue;

            for (int next_v = 0; next_v < n; ++next_v) {
                if (mask & (1 << next_v)) continue;
                if (!g->adj_matrix[v][next_v]) continue;

                int next_mask = mask | (1 << next_v);
                dp[next_mask][next_v] = true;
                parent[next_mask][next_v] = v;
            }
        }
    }

    int full_mask = num_states - 1;
    int last_v = -1;

    for (int v = 1; v < n; ++v) {
        if (dp[full_mask][v] && g->adj_matrix[v][0]) {
            last_v = v;
            break;
        }
    }

    bool success = false;
    if (last_v != -1) {
        success = true;
        if (out_path) {
            int curr_mask = full_mask;
            int curr_v = last_v;
            for (int step = n - 1; step >= 1; --step) {
                out_path[step] = curr_v;
                int prev_v = parent[curr_mask][curr_v];
                curr_mask ^= (1 << curr_v);
                curr_v = prev_v;
            }
            out_path[0] = 0;
        }
    }

    for (int i = 0; i < num_states; ++i) {
        free(dp[i]);
        free(parent[i]);
    }
    free(dp);
    free(parent);

    return success;
}
