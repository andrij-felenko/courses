#include <iostream>
#include <vector>
#include <queue>
#include <limits>
#include <optional>

namespace graph {

struct JEdge {
    int src;
    int dest;
    long long weight;
};

class JohnsonAlgorithm {
public:
    static constexpr long long INF = std::numeric_limits<long long>::max();

    static std::optional<std::vector<std::vector<long long>>> compute(int V, const std::vector<JEdge>& edges) {
        // Крок 1: Додавання супер-джерела з вагою 0 до всіх вершин
        std::vector<JEdge> super_edges = edges;
        int super_source = V;
        for (int i = 0; i < V; ++i) {
            super_edges.push_back({super_source, i, 0});
        }

        // Крок 2: Запуск Беллмана-Форда для обчислення потенціалів h[]
        std::vector<long long> h(V + 1, INF);
        h[super_source] = 0;

        for (int iter = 0; iter < V; ++iter) {
            bool updated = false;
            for (const auto& edge : super_edges) {
                if (h[edge.src] != INF && h[edge.src] + edge.weight < h[edge.dest]) {
                    h[edge.dest] = h[edge.src] + edge.weight;
                    updated = true;
                }
            }
            if (!updated) break;
        }

        // Перевірка на від'ємний цикл
        for (const auto& edge : super_edges) {
            if (h[edge.src] != INF && h[edge.src] + edge.weight < h[edge.dest]) {
                return std::nullopt; // Знайдено від'ємний цикл
            }
        }

        // Крок 3: Перезважування ребер w_hat(u, v) = w(u, v) + h(u) - h(v)
        std::vector<std::vector<std::pair<int, long long>>> adj(V);
        for (const auto& edge : edges) {
            long long reweighted = edge.weight + h[edge.src] - h[edge.dest];
            adj[edge.src].push_back({edge.dest, reweighted});
        }

        // Крок 4: Запуск Дейкстри від кожної вершини
        std::vector<std::vector<long long>> all_dist(V, std::vector<long long>(V, INF));

        for (int s = 0; s < V; ++s) {
            std::priority_queue<std::pair<long long, int>, 
                                std::vector<std::pair<long long, int>>, 
                                std::greater<std::pair<long long, int>>> pq;
            all_dist[s][s] = 0;
            pq.push({0, s});

            while (!pq.empty()) {
                auto [d, u] = pq.top();
                pq.pop();

                if (d > all_dist[s][u]) continue;

                for (const auto& [v, w_hat] : adj[u]) {
                    if (all_dist[s][u] + w_hat < all_dist[s][v]) {
                        all_dist[s][v] = all_dist[s][u] + w_hat;
                        pq.push({all_dist[s][v], v});
                    }
                }
            }

            // Відновлення справжніх відстаней: d_orig(u, v) = d_hat(u, v) - h(u) + h(v)
            for (int v = 0; v < V; ++v) {
                if (all_dist[s][v] != INF) {
                    all_dist[s][v] += h[v] - h[s];
                }
            }
        }

        return all_dist;
    }
};

} // namespace graph
