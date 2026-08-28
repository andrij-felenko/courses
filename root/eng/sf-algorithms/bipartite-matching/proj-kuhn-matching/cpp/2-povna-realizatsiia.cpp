/*
 * Алгоритм Куна та Хопкрофта–Карпа мовою C++20.
 * Включає ідіоматичний RAII клас BipartiteGraph.
 */

#include <iostream>
#include <vector>
#include <queue>
#include <algorithm>
#include <cstdint>
#include <limits>

class BipartiteGraph {
public:
    BipartiteGraph(std::size_t u_size, std::size_t v_size)
        : u_size_(u_size), v_size_(v_size), adj_(u_size) {}

    void add_edge(std::size_t u, std::size_t v) {
        if (u < u_size_ && v < v_size_) {
            adj_[u].push_back(v);
        }
    }

    [[nodiscard]] std::size_t u_size() const noexcept { return u_size_; }
    [[nodiscard]] std::size_t v_size() const noexcept { return v_size_; }

    // Обчислення максимального паросполучення алгоритмом Куна
    [[nodiscard]] std::pair<std::size_t, std::vector<int>> solve_kuhn() const {
        std::vector<int> match(v_size_, -1);
        std::vector<int> used_token(u_size_, 0);
        int current_token = 0;

        auto dfs = [&](auto self, std::size_t u) -> bool {
            if (used_token[u] == current_token) return false;
            used_token[u] = current_token;

            for (std::size_t v : adj_[u]) {
                if (match[v] == -1 || self(self, static_cast<std::size_t>(match[v]))) {
                    match[v] = static_cast<int>(u);
                    return true;
                }
            }
            return false;
        };

        std::size_t max_matching = 0;
        for (std::size_t u = 0; u < u_size_; ++u) {
            ++current_token;
            if (dfs(dfs, u)) {
                ++max_matching;
            }
        }
        return {max_matching, match};
    }

    // Обчислення максимального паросполучення алгоритмом Хопкрофта–Карпа O(E * sqrt(V))
    [[nodiscard]] std::pair<std::size_t, std::vector<int>> solve_hopcroft_karp() const {
        std::vector<int> match_u(u_size_, -1);
        std::vector<int> match_v(v_size_, -1);
        std::vector<int> dist(u_size_, 0);

        constexpr int INF = std::numeric_limits<int>::max();

        auto bfs = [&]() -> bool {
            std::queue<std::size_t> q;
            for (std::size_t u = 0; u < u_size_; ++u) {
                if (match_u[u] == -1) {
                    dist[u] = 0;
                    q.push(u);
                } else {
                    dist[u] = INF;
                }
            }

            bool found_free_v = false;
            while (!q.empty()) {
                std::size_t u = q.front();
                q.pop();

                for (std::size_t v : adj_[u]) {
                    if (match_v[v] == -1) {
                        found_free_v = true;
                    } else if (dist[match_v[v]] == INF) {
                        dist[match_v[v]] = dist[u] + 1;
                        q.push(static_cast<std::size_t>(match_v[v]));
                    }
                }
            }
            return found_free_v;
        };

        auto dfs = [&](auto self, std::size_t u) -> bool {
            for (std::size_t v : adj_[u]) {
                if (match_v[v] == -1 || 
                   (dist[match_v[v]] == dist[u] + 1 && self(self, static_cast<std::size_t>(match_v[v])))) {
                    match_v[v] = static_cast<int>(u);
                    match_u[u] = static_cast<int>(v);
                    return true;
                }
            }
            dist[u] = INF;
            return false;
        };

        std::size_t max_matching = 0;
        while (bfs()) {
            for (std::size_t u = 0; u < u_size_; ++u) {
                if (match_u[u] == -1 && dfs(dfs, u)) {
                    ++max_matching;
                }
            }
        }
        return {max_matching, match_v};
    }

private:
    std::size_t u_size_;
    std::size_t v_size_;
    std::vector<std::vector<std::size_t>> adj_;
};

int main() {
    BipartiteGraph g(4, 4);
    g.add_edge(0, 0);
    g.add_edge(0, 1);
    g.add_edge(1, 1);
    g.add_edge(1, 2);
    g.add_edge(2, 0);
    g.add_edge(2, 2);
    g.add_edge(3, 3);

    auto [kuhn_size, kuhn_match] = g.solve_kuhn();
    std::cout << "[C++] Кун: розмір = " << kuhn_size << "\n";

    auto [hk_size, hk_match] = g.solve_hopcroft_karp();
    std::cout << "[C++] Хопкрофт–Карпа: розмір = " << hk_size << "\n";

    for (std::size_t v = 0; v < g.v_size(); ++v) {
        if (hk_match[v] != -1) {
            std::cout << "  v" << v << " <-> u" << hk_match[v] << "\n";
        }
    }
    return 0;
}
