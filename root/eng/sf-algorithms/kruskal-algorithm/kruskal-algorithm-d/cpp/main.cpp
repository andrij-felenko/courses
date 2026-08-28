#include <vector>
#include <span>
#include <algorithm>
#include <cstdint>
#include <numeric>
#include <expected>

struct Edge {
    uint32_t u{0};
    uint32_t v{0};
    int64_t weight{0};

    [[nodiscard]] constexpr bool operator<(const Edge& other) const noexcept {
        return weight < other.weight;
    }
};

class DisjointSet {
public:
    explicit DisjointSet(uint32_t size)
        : parent_(size), rank_(size, 0), components_(size) {
        std::iota(parent_.begin(), parent_.end(), 0);
    }

    [[nodiscard]] uint32_t find(uint32_t node) noexcept {
        uint32_t root = node;
        while (root != parent_[root]) {
            root = parent_[root];
        }
        // Двопрохідне стиснення шляхів без рекурсії
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
            return false; // Виявлено замкнений цикл
        }

        if (rank_[root_u] < rank_[root_v]) {
            parent_[root_u] = root_v;
        } else if (rank_[root_u] > rank_[root_v]) {
            parent_[root_v] = root_u;
        } else {
            parent_[root_v] = root_u;
            ++rank_[root_u];
        }
        --components_;
        return true;
    }

    [[nodiscard]] uint32_t component_count() const noexcept {
        return components_;
    }

private:
    std::vector<uint32_t> parent_;
    std::vector<uint8_t> rank_;
    uint32_t components_;
};

struct MstResult {
    std::vector<Edge> edges;
    int64_t total_weight{0};
    bool is_connected{false};
};

enum class GraphError {
    InvalidVertexIndex,
    EmptyGraph
};

[[nodiscard]] std::expected<MstResult, GraphError>
build_kruskal_mst(uint32_t num_vertices, std::span<Edge> edges) {
    if (num_vertices == 0) {
        return MstResult{{}, 0, true};
    }

    for (const auto& edge : edges) {
        if (edge.u >= num_vertices || edge.v >= num_vertices) {
            return std::unexpected(GraphError::InvalidVertexIndex);
        }
    }

    // Фаза 1: Сортування масиву ребер за зростанням ваги
    std::ranges::sort(edges);

    // Фаза 2: Ініціалізація DSU
    DisjointSet dsu(num_vertices);

    MstResult result;
    result.edges.reserve(num_vertices - 1);

    // Фаза 3: Жадібне об'єднання з раннім виходом
    for (const auto& edge : edges) {
        if (dsu.unite(edge.u, edge.v)) {
            result.edges.push_back(edge);
            result.total_weight += edge.weight;

            if (result.edges.size() == num_vertices - 1) {
                break;
            }
        }
    }

    result.is_connected = (result.edges.size() == num_vertices - 1);
    return result;
}
