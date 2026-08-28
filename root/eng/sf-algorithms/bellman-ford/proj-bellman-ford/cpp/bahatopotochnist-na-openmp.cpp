#include <vector>
#include <atomic>
#include <limits>
#include <omp.h>

struct Edge {
    int src;
    int dest;
    long long weight;
};

void parallel_bellman_ford_cpp(int V, const std::vector<Edge>& edges, std::vector<long long>& dist) {
    std::atomic<bool> updated{false};

    for (int iter = 0; iter < V - 1; ++iter) {
        updated = false;
        #pragma omp parallel for schedule(static)
        for (size_t i = 0; i < edges.size(); ++i) {
            int u = edges[i].src;
            int v = edges[i].dest;
            long long w = edges[i].weight;

            if (dist[u] != std::numeric_limits<long long>::max()) {
                long long new_dist = dist[u] + w;
                // Критичний секційний вибір для гарантії атомарності
                if (new_dist < dist[v]) {
                    #pragma omp critical
                    {
                        if (new_dist < dist[v]) {
                            dist[v] = new_dist;
                            updated = true;
                        }
                    }
                }
            }
        }
        if (!updated) break;
    }
}
