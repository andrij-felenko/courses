#include <iostream>
#include <vector>
#include <span>
#include <numeric>
#include <cstdint>

struct RawEdge {
    int u;
    int v;
    int64_t weight;
};

class DisjointSetUnion {
public:
    explicit DisjointSetUnion(int n) : parent_(n), rank_(n, 0), count_(n) {
        std::iota(parent_.begin(), parent_.end(), 0);
    }

    int find(int i) noexcept {
        if (parent_[i] == i) return i;
        return parent_[i] = find(parent_[i]);
    }

    bool unite(int i, int j) noexcept {
        int root_i = find(i);
        int root_j = find(j);
        if (root_i == root_j) return false;

        if (rank_[root_i] < rank_[root_j]) {
            parent_[root_i] = root_j;
        } else if (rank_[root_i] > rank_[root_j]) {
            parent_[root_j] = root_i;
        } else {
            parent_[root_j] = root_i;
            rank_[root_i]++;
        }
        count_--;
        return true;
    }

    [[nodiscard]] int count() const noexcept { return count_; }

private:
    std::vector<int> parent_;
    std::vector<int> rank_;
    int count_;
};

[[nodiscard]] MstResult boruvka_mst(int num_vertices, std::span<const RawEdge> edges) {
    if (num_vertices <= 0) return {};

    MstResult result;
    result.edges.reserve(num_vertices > 1 ? num_vertices - 1 : 0);

    DisjointSetUnion dsu(num_vertices);
    std::vector<int> cheapest(num_vertices, -1);

    while (dsu.count() > 1) {
        std::fill(cheapest.begin(), cheapest.end(), -1);
        bool progress = false;

        for (int i = 0; i < static_cast<int>(edges.size()); ++i) {
            const auto& edge = edges[i];
            const int set_u = dsu.find(edge.u);
            const int set_v = dsu.find(edge.v);

            if (set_u == set_v) continue;

            if (cheapest[set_u] == -1 || edge.weight < edges[cheapest[set_u]].weight) {
                cheapest[set_u] = i;
            }
            if (cheapest[set_v] == -1 || edge.weight < edges[cheapest[set_v]].weight) {
                cheapest[set_v] = i;
            }
        }

        for (int i = 0; i < num_vertices; ++i) {
            if (cheapest[i] != -1) {
                const int edge_idx = cheapest[i];
                const auto& edge = edges[edge_idx];
                if (dsu.unite(edge.u, edge.v)) {
                    result.edges.push_back(MstEdge{edge.u, edge.v, edge.weight});
                    result.total_weight += edge.weight;
                    progress = true;
                }
            }
        }

        if (!progress) break;
    }

    result.is_connected = (dsu.count() == 1);
    return result;
}
