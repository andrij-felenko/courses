#include <iostream>
#include <vector>
#include <optional>
#include <limits>
#include <algorithm>
#include <queue>

namespace graph {

struct Edge {
    int src;
    int dest;
    long long weight;
};

struct PathResult {
    std::vector<long long> dist;
    std::vector<int> parent;
    std::optional<std::vector<int>> negative_cycle;
};

class BellmanFord {
public:
    static constexpr long long INF = std::numeric_limits<long long>::max();

    // Класичний Беллман-Форд із вилученням циклу
    static PathResult compute(int num_vertices, const std::vector<Edge>& edges, int start_node) {
        std::vector<long long> dist(num_vertices, INF);
        std::vector<int> parent(num_vertices, -1);
        dist[start_node] = 0;

        // V - 1 раундів релаксації
        for (int iter = 0; iter < num_vertices - 1; ++iter) {
            bool updated = false;
            for (const auto& edge : edges) {
                if (dist[edge.src] != INF && dist[edge.src] + edge.weight < dist[edge.dest]) {
                    dist[edge.dest] = dist[edge.src] + edge.weight;
                    parent[edge.dest] = edge.src;
                    updated = true;
                }
            }
            if (!updated) {
                break;
            }
        }

        // Детекція від'ємного циклу на V-му раунді
        int cycle_node = -1;
        for (const auto& edge : edges) {
            if (dist[edge.src] != INF && dist[edge.src] + edge.weight < dist[edge.dest]) {
                cycle_node = edge.dest;
                parent[edge.dest] = edge.src;
                break;
            }
        }

        if (cycle_node != -1) {
            // Відкручуємо назад на V кроків для 100% занурення в цикл
            for (int i = 0; i < num_vertices; ++i) {
                cycle_node = parent[cycle_node];
            }

            std::vector<int> cycle;
            for (int curr = cycle_node;; curr = parent[curr]) {
                cycle.push_back(curr);
                if (curr == cycle_node && cycle.size() > 1) {
                    break;
                }
            }
            std::reverse(cycle.begin(), cycle.end());
            return {std::move(dist), std::move(parent), std::move(cycle)};
        }

        return {std::move(dist), std::move(parent), std::nullopt};
    }

    // Оптимізований алгоритм SPFA (Shortest Path Faster Algorithm)
    static PathResult compute_spfa(int num_vertices, const std::vector<std::vector<std::pair<int, long long>>>& adj, int start_node) {
        std::vector<long long> dist(num_vertices, INF);
        std::vector<int> parent(num_vertices, -1);
        std::vector<int> relax_count(num_vertices, 0);
        std::vector<bool> in_queue(num_vertices, false);
        std::queue<int> q;

        dist[start_node] = 0;
        q.push(start_node);
        in_queue[start_node] = true;

        int cycle_node = -1;

        while (!q.empty()) {
            int u = q.front();
            q.pop();
            in_queue[u] = false;

            for (const auto& [v, weight] : adj[u]) {
                if (dist[u] != INF && dist[u] + weight < dist[v]) {
                    dist[v] = dist[u] + weight;
                    parent[v] = u;

                    if (!in_queue[v]) {
                        q.push(v);
                        in_queue[v] = true;
                        relax_count[v]++;

                        if (relax_count[v] >= num_vertices) {
                            cycle_node = v;
                            break;
                        }
                    }
                }
            }
            if (cycle_node != -1) break;
        }

        if (cycle_node != -1) {
            for (int i = 0; i < num_vertices; ++i) {
                cycle_node = parent[cycle_node];
            }
            std::vector<int> cycle;
            for (int curr = cycle_node;; curr = parent[curr]) {
                cycle.push_back(curr);
                if (curr == cycle_node && cycle.size() > 1) break;
            }
            std::reverse(cycle.begin(), cycle.end());
            return {std::move(dist), std::move(parent), std::move(cycle)};
        }

        return {std::move(dist), std::move(parent), std::nullopt};
    }
};

} // namespace graph

int main() {
    int V = 5;
    std::vector<graph::Edge> edges = {
        {0, 1, 4},
        {0, 2, 5},
        {1, 3, 3},
        {2, 1, -6},
        {3, 2, 1}
    };

    auto result = graph::BellmanFord::compute(V, edges, 0);

    if (result.negative_cycle) {
        std::cout << "Виявлено від'ємний цикл: ";
        for (int node : *result.negative_cycle) {
            std::cout << node << " ";
        }
        std::cout << "\n";
    } else {
        std::cout << "Найкоротші відстані від вершини 0:\n";
        for (int i = 0; i < V; ++i) {
            if (result.dist[i] == graph::BellmanFord::INF) {
                std::cout << "Вузол " << i << ": недосяжний\n";
            } else {
                std::cout << "Вузол " << i << ": " << result.dist[i] << "\n";
            }
        }
    }

    return 0;
}
