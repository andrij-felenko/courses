#include <omp.h>
#include <stdbool.h>
#include <limits.h>

void parallel_bellman_ford_step(int num_edges, const Edge* edges, long long* dist, bool* updated) {
    #pragma omp parallel for
    for (int e = 0; e < num_edges; ++e) {
        int u = edges[e].src;
        int v = edges[e].dest;
        long long w = edges[e].weight;

        if (dist[u] != LLONG_MAX) {
            long long new_d = dist[u] + w;
            if (new_d < dist[v]) {
                #pragma omp critical
                {
                    if (new_d < dist[v]) {
                        dist[v] = new_d;
                        *updated = true;
                    }
                }
            }
        }
    }
}
