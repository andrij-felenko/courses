#include <iostream>
#include <vector>
#include <numeric>
#include <memory>
#include <algorithm>
#include <optional>
#include <utility>

class DisjointSetUnion {
public:
    explicit DisjointSetUnion(std::size_t n)
        : parent_(n), rank_(n, 0), side_(n, 0) {
        std::iota(parent_.begin(), parent_.end(), 0);
    }

    std::size_t find(std::size_t v) {
        if (parent_[v] == v) return v;
        std::size_t root = find(parent_[v]);
        side_[v] ^= side_[parent_[v]];
        parent_[v] = root;
        return root;
    }

    bool add_conflict(std::size_t u, std::size_t v) {
        std::size_t root_u = find(u);
        std::size_t root_v = find(v);

        if (root_u == root_v) {
            return side_[u] != side_[v];
        }

        if (rank_[root_u] < rank_[root_v]) {
            std::swap(root_u, root_v);
            std::swap(u, v);
        }

        parent_[root_v] = root_u;
        side_[root_v] = side_[u] ^ side_[v] ^ 1;
        if (rank_[root_u] == rank_[root_v]) {
            rank_[root_u]++;
        }
        return true;
    }

private:
    std::vector<std::size_t> parent_;
    std::vector<int> rank_;
    std::vector<int> side_;
};

struct Edge {
    std::size_t to;
    std::size_t id;
};

class PlanarityTester {
public:
    explicit PlanarityTester(std::size_t num_vertices)
        : num_vertices_(num_vertices), adj_(num_vertices) {}

    void add_edge(std::size_t u, std::size_t v) {
        std::size_t id = edge_count_++;
        adj_[u].push_back({v, id});
        adj_[v].push_back({u, id});
    }

    [[nodiscard]] bool is_planar() {
        if (num_vertices_ >= 3 && edge_count_ > 3 * num_vertices_ - 6) {
            return false; // Відсікання за формулою Ейлера
        }
        if (num_vertices_ <= 4) {
            return true;
        }

        height_.assign(num_vertices_, 0);
        low_.assign(num_vertices_, 0);
        low2_.assign(num_vertices_, 0);
        visited_.assign(num_vertices_, false);
        dsu_ = std::make_unique<DisjointSetUnion>(edge_count_);

        for (std::size_t i = 0; i < num_vertices_; ++i) {
            if (!visited_[i]) {
                timer_ = 0;
                dfs_orient(i, std::nullopt);
                if (!dfs_conflicts(i, std::nullopt)) {
                    return false;
                }
            }
        }
        return true;
    }

private:
    std::size_t num_vertices_;
    std::size_t edge_count_{0};
    std::vector<std::vector<Edge>> adj_;

    std::vector<int> height_;
    std::vector<int> low_;
    std::vector<int> low2_;
    std::vector<bool> visited_;
    int timer_{0};
    std::unique_ptr<DisjointSetUnion> dsu_;

    void dfs_orient(std::size_t u, std::optional<std::size_t> p_edge) {
        visited_[u] = true;
        height_[u] = ++timer_;
        low_[u] = height_[u];
        low2_[u] = height_[u];

        for (const auto& [v, edge_id] : adj_[u]) {
            if (p_edge && edge_id == *p_edge) continue;

            if (visited_[v]) {
                if (height_[v] < low_[u]) {
                    low2_[u] = low_[u];
                    low_[u] = height_[v];
                } else if (height_[v] > low_[u] && height_[v] < low2_[u]) {
                    low2_[u] = height_[v];
                }
            } else {
                dfs_orient(v, edge_id);
                if (low_[v] < low_[u]) {
                    low2_[u] = std::min(low_[u], low2_[v]);
                    low_[u] = low_[v];
                } else if (low_[v] > low_[u] && low_[v] < low2_[u]) {
                    low2_[u] = low_[v];
                }
            }
        }
    }

    bool dfs_conflicts(std::size_t u, std::optional<std::size_t> p_edge) {
        for (const auto& [v, edge_id] : adj_[u]) {
            if (p_edge && edge_id == *p_edge) continue;

            if (height_[v] > height_[u]) {
                if (!dfs_conflicts(v, edge_id)) return false;
            } else if (height_[v] < height_[u]) {
                if (p_edge && low2_[u] >= height_[v]) {
                    if (!dsu_->add_conflict(edge_id, *p_edge)) {
                        return false; // Знайдено топологічний конфлікт Куратовського
                    }
                }
            }
        }
        return true;
    }
};

int main() {
    // 1. Повний граф K5 (5 вершин, 10 ребер)
    PlanarityTester k5(5);
    for (std::size_t i = 0; i < 5; ++i) {
        for (std::size_t j = i + 1; j < 5; ++j) {
            k5.add_edge(i, j);
        }
    }
    std::cout << "K5 планарність: " << (k5.is_planar() ? "Так" : "Ні") << "\n";

    // 2. Двочастковий граф K3,3 (6 вершин, 9 ребер)
    PlanarityTester k33(6);
    for (std::size_t i = 0; i < 3; ++i) {
        for (std::size_t j = 3; j < 6; ++j) {
            k33.add_edge(i, j);
        }
    }
    std::cout << "K3,3 планарність: " << (k33.is_planar() ? "Так" : "Ні") << "\n";

    // 3. Планарна сітка 3x3 (9 вершин, 12 ребер)
    PlanarityTester grid(9);
    for (std::size_t r = 0; r < 3; ++r) {
        for (std::size_t c = 0; c < 3; ++c) {
            std::size_t u = r * 3 + c;
            if (c + 1 < 3) grid.add_edge(u, u + 1);
            if (r + 1 < 3) grid.add_edge(u, u + 3);
        }
    }
    std::cout << "Сітка 3x3 планарність: " << (grid.is_planar() ? "Так" : "Ні") << "\n";

    return 0;
}
