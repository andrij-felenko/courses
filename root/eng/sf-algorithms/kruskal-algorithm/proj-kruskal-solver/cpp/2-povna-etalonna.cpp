#include <vector>
#include <span>
#include <algorithm>
#include <cstdint>
#include <numeric>
#include <expected>
#include <optional>

struct Edge {
    uint32_t u{0};
    uint32_t v{0};
    int64_t weight{0};

    constexpr bool operator<(const Edge& other) const noexcept {
        return weight < other.weight;
    }
};

class DisjointSetUnion {
public:
    explicit DisjointSetUnion(uint32_t n)
        : parent_(n), rank_(n, 0), num_sets_(n) {
        std::iota(parent_.begin(), parent_.end(), 0);
    }

    [[nodiscard]] uint32_t find(uint32_t node) noexcept {
        uint32_t root = node;
        while (root != parent_[root]) {
            root = parent_[root];
        }
        // Стиснення шляху (двопрохідний варіант без рекурсії)
        uint32_t curr = node;
        while (curr != root) {
            uint32_t nxt = parent_[curr];
            parent_[curr] = root;
            curr = nxt;
        }
        return root;
    }

    bool unite(uint32_t u, uint32_t v) noexcept {
        uint32_t root_u = find(u);
        uint32_t root_v = find(v);
        if (root_u == root_v) {
            return false;
        }

        if (rank_[root_u] < rank_[root_v]) {
            parent_[root_u] = root_v;
        } else if (rank_[root_u] > rank_[root_v]) {
            parent_[root_v] = root_u;
        } else {
            parent_[root_v] = root_u;
            ++rank_[root_u];
        }
        --num_sets_;
        return true;
    }

    [[nodiscard]] uint32_t component_count() const noexcept {
        return num_sets_;
    }

private:
    std::vector<uint32_t> parent_;
    std::vector<uint8_t> rank_;
    uint32_t num_sets_;
};

struct KruskalResult {
    std::vector<Edge> mst_edges;
    int64_t total_weight{0};
    bool is_fully_connected{false};
};

enum class KruskalError {
    InvalidVertexIndex,
    EmptyGraph
};

[[nodiscard]] std::expected<KruskalResult, KruskalError>
compute_kruskal_mst(uint32_t num_vertices, std::span<Edge> edges) {
    if (num_vertices == 0) {
        return KruskalResult{{}, 0, true};
    }

    // Перевірка коректності індексів вершин
    for (const auto& edge : edges) {
        if (edge.u >= num_vertices || edge.v >= num_vertices) {
            return std::unexpected(KruskalError::InvalidVertexIndex);
        }
    }

    // Крок 1: Швидке сортування масиву ребер за зростанням ваги
    std::ranges::sort(edges);

    // Крок 2: Ініціалізація DSU
    DisjointSetUnion dsu(num_vertices);

    KruskalResult result;
    result.mst_edges.reserve(num_vertices - 1);

    // Крок 3: Жадібний вибір ребер з раннім виходом
    for (const auto& edge : edges) {
        if (dsu.unite(edge.u, edge.v)) {
            result.mst_edges.push_back(edge);
            result.total_weight += edge.weight;

            if (result.mst_edges.size() == num_vertices - 1) {
                break;
            }
        }
    }

    result.is_fully_connected = (result.mst_edges.size() == num_vertices - 1);
    return result;
}
