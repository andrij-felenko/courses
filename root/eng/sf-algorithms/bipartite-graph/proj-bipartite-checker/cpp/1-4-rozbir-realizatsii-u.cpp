// C++ Implementation: Idiomatic BFS 2-coloring with std::optional
#include <vector>
#include <queue>
#include <optional>
#include <iostream>
#include <cstddef>

class BipartiteChecker {
public:
    explicit BipartiteChecker(std::size_t vertices) : adj_(vertices) {}

    void add_edge(std::size_t u, std::size_t v) {
        adj_.at(u).push_back(v);
        adj_.at(v).push_back(u);
    }

    // Повертає вектор кольорів (0 або 1) або std::nullopt у разі непарного циклу
    [[nodiscard]] std::optional<std::vector<int>> check_bipartite() const {
        std::size_t n = adj_.size();
        std::vector<int> colors(n, -1);

        for (std::size_t start = 0; start < n; ++start) {
            if (colors[start] != -1) continue;

            std::queue<std::size_t> q;
            colors[start] = 0;
            q.push(start);

            while (!q.empty()) {
                std::size_t u = q.front();
                q.pop();

                int next_color = 1 - colors[u];

                for (std::size_t v : adj_[u]) {
                    if (colors[v] == -1) {
                        colors[v] = next_color;
                        q.push(v);
                    } else if (colors[v] == colors[u]) {
                        return std::nullopt; // Знайдено непарний цикл!
                    }
                }
            }
        }
        return colors;
    }

private:
    std::vector<std::vector<std::size_t>> adj_;
};
