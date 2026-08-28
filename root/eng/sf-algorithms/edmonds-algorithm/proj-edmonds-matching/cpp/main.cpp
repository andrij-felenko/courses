#include <iostream>
#include <vector>
#include <queue>
#include <numeric>
#include <algorithm>
#include <optional>

class EdmondsMatchingSolver {
public:
    explicit EdmondsMatchingSolver(size_t vertices)
        : num_vertices_(vertices),
          adj_(vertices),
          match_(vertices, -1),
          parent_(vertices, -1),
          base_(vertices),
          type_(vertices, VertexType::Unvisited),
          visited_lca_(vertices, 0) {}

    void add_edge(int u, int v) {
        adj_[u].push_back(v);
        adj_[v].push_back(u);
    }

    int solve_max_matching() {
        std::fill(match_.begin(), match_.end(), -1);
        std::fill(visited_lca_.begin(), visited_lca_.end(), 0);
        timer_lca_ = 0;

        int matching_size = 0;
        for (size_t i = 0; i < num_vertices_; ++i) {
            if (match_[i] == -1) {
                if (bfs_augment(static_cast<int>(i))) {
                    matching_size++;
                }
            }
        }
        return matching_size;
    }

    [[nodiscard]] const std::vector<int>& get_matching() const noexcept {
        return match_;
    }

private:
    enum class VertexType { Unvisited = -1, Even = 0, Odd = 1 };

    size_t num_vertices_;
    std::vector<std::vector<int>> adj_;
    std::vector<int> match_;
    std::vector<int> parent_;
    std::vector<int> base_;
    std::vector<VertexType> type_;
    std::vector<int> visited_lca_;
    int timer_lca_{0};

    int dsu_find(int u) {
        if (base_[u] == u) return u;
        return base_[u] = dsu_find(base_[u]);
    }

    int find_lca(int u, int v) {
        timer_lca_++;
        u = dsu_find(u);
        v = dsu_find(v);

        while (true) {
            if (u != -1) {
                if (visited_lca_[u] == timer_lca_) return u;
                visited_lca_[u] = timer_lca_;
                u = (match_[u] != -1) ? dsu_find(parent_[match_[u]]) : -1;
            }
            std::swap(u, v);
        }
    }

    void mark_blossom(int u, int v, int lca_node, std::queue<int>& q) {
        while (dsu_find(u) != lca_node) {
            parent_[u] = v;
            v = match_[u];

            if (type_[v] == VertexType::Odd) {
                type_[v] = VertexType::Even;
                q.push(v);
            }

            base_[u] = lca_node;
            base_[v] = lca_node;
            u = parent_[v];
        }
    }

    bool bfs_augment(int start_root) {
        std::iota(base_.begin(), base_.end(), 0);
        std::fill(parent_.begin(), parent_.end(), -1);
        std::fill(type_.begin(), type_.end(), VertexType::Unvisited);

        std::queue<int> q;
        type_[start_root] = VertexType::Even;
        q.push(start_root);

        while (!q.empty()) {
            int u = q.front();
            q.pop();

            for (int v : adj_[u]) {
                if (dsu_find(u) == dsu_find(v) || type_[v] == VertexType::Odd) {
                    continue;
                }

                if (type_[v] == VertexType::Unvisited) {
                    parent_[v] = u;
                    type_[v] = VertexType::Odd;

                    if (match_[v] == -1) {
                        /* Відновлення та інвертування шляху */
                        int curr = v;
                        while (curr != -1) {
                            int p = parent_[curr];
                            int next_p = (p != -1) ? match_[p] : -1;
                            match_[curr] = p;
                            match_[p] = curr;
                            curr = next_p;
                        }
                        return true;
                    }

                    type_[match_[v]] = VertexType::Even;
                    q.push(match_[v]);
                } else if (type_[v] == VertexType::Even) {
                    int lca_node = find_lca(u, v);
                    mark_blossom(u, v, lca_node, q);
                    mark_blossom(v, u, lca_node, q);
                }
            }
        }
        return false;
    }
};

int main() {
    EdmondsMatchingSolver solver(5);
    /* Граф С5: 0-1-2-3-4-0 */
    solver.add_edge(0, 1);
    solver.add_edge(1, 2);
    solver.add_edge(2, 3);
    solver.add_edge(3, 4);
    solver.add_edge(4, 0);

    int count = solver.solve_max_matching();
    std::cout << "C++ Solver: Максимальне паросполучення = " << count << std::endl;

    const auto& matching = solver.get_matching();
    for (size_t i = 0; i < matching.size(); ++i) {
        if (matching[i] > static_cast<int>(i)) {
            std::cout << "Ребро паросполучення: (" << i << ", " << matching[i] << ")\n";
        }
    }
    return 0;
}
