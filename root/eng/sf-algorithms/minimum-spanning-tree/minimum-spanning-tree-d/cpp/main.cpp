#include <vector>
#include <queue>
#include <span>
#include <cstdint>
#include <limits>

struct Edge {
    int to;
    int64_t weight;
};

struct MstEdge {
    int u;
    int v;
    int64_t weight;
};

struct MstResult {
    std::vector<MstEdge> edges;
    int64_t total_weight{0};
    bool is_connected{false};
};

class Graph {
public:
    explicit Graph(int num_vertices) : adj_(num_vertices) {}

    void add_edge(int u, int v, int64_t weight) {
        adj_[u].push_back(Edge{v, weight});
        adj_[v].push_back(Edge{u, weight});
    }

    [[nodiscard]] int num_vertices() const noexcept {
        return static_cast<int>(adj_.size());
    }

    [[nodiscard]] std::span<const Edge> neighbors(int u) const noexcept {
        return adj_[u];
    }

private:
    std::vector<std::vector<Edge>> adj_;
};

[[nodiscard]] MstResult prim_mst(const Graph& graph) {
    const int n = graph.num_vertices();
    if (n == 0) return {};

    MstResult result;
    result.edges.reserve(n > 1 ? n - 1 : 0);

    std::vector<int64_t> min_key(n, std::numeric_limits<int64_t>::max());
    std::vector<int> parent(n, -1);
    std::vector<bool> in_mst(n, false);

    // Min-Priority Queue зберігає пари (вага, вершина)
    using QueueNode = std::pair<int64_t, int>;
    std::priority_queue<QueueNode, std::vector<QueueNode>, std::greater<>> pq;

    min_key[0] = 0;
    pq.emplace(0, 0);
    int visited_count = 0;

    while (!pq.empty()) {
        const auto [weight, u] = pq.top();
        pq.pop();

        if (in_mst[u]) continue;

        in_mst[u] = true;
        visited_count++;

        if (parent[u] != -1) {
            result.edges.push_back(MstEdge{parent[u], u, weight});
            result.total_weight += weight;
        }

        for (const auto& [v, w] : graph.neighbors(u)) {
            if (!in_mst[v] && w < min_key[v]) {
                min_key[v] = w;
                parent[v] = u;
                pq.emplace(w, v);
            }
        }
    }

    result.is_connected = (visited_count == n);
    return result;
}
