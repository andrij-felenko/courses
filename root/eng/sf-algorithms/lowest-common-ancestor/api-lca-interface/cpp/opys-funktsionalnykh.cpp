#include <vector>
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <stdexcept>
#include <iostream>

namespace math::graph {

template <typename WeightType = int64_t>
class AdvancedLCA {
private:
    int n_;
    int logn_;
    int root_;
    bool is_built_;

    std::vector<int> depth_;
    std::vector<WeightType> dist_root_;
    std::vector<int> tin_;
    std::vector<int> tout_;
    int timer_;

    struct EdgeData {
        int to;
        WeightType weight;
    };

    std::vector<std::vector<EdgeData>> adj_;
    std::vector<std::vector<int>> up_;

    void dfs(int u, int p, int d, WeightType w_sum) {
        tin_[u] = ++timer_;
        depth_[u] = d;
        dist_root_[u] = w_sum;
        up_[u][0] = p;

        for (int k = 1; k < logn_; ++k) {
            up_[u][k] = up_[up_[u][k - 1]][k - 1];
        }

        for (const auto& edge : adj_[u]) {
            if (edge.to != p) {
                dfs(edge.to, u, d + 1, w_sum + edge.weight);
            }
        }
        tout_[u] = ++timer_;
    }

public:
    explicit AdvancedLCA(int num_nodes)
        : n_(num_nodes),
          logn_(static_cast<int>(std::ceil(std::log2(num_nodes + 1))) + 2),
          root_(1),
          is_built_(false),
          depth_(num_nodes + 1, 0),
          dist_root_(num_nodes + 1, 0),
          tin_(num_nodes + 1, 0),
          tout_(num_nodes + 1, 0),
          timer_(0),
          adj_(num_nodes + 1),
          up_(num_nodes + 1, std::vector<int>(logn_, 0)) {}

    void add_edge(int u, int v, WeightType weight = 1) {
        if (is_built_) {
            throw std::logic_error("Неможливо додати ребро: структура вже побудована.");
        }
        if (u < 1 || u > n_ || v < 1 || v > n_) {
            throw std::out_of_range("Індекс вершини вийшов за межі [1..N].");
        }
        adj_[u].push_back({v, weight});
        adj_[v].push_back({u, weight});
    }

    void build(int root = 1) {
        root_ = root;
        timer_ = 0;
        dfs(root_, root_, 0, 0);
        is_built_ = true;
    }

    [[nodiscard]] bool is_ancestor(int u, int v) const {
        if (!is_built_) throw std::logic_error("Структура не ініціалізована. Викличте build().");
        return tin_[u] <= tin_[v] && tout_[u] >= tout_[v];
    }

    [[nodiscard]] int query(int u, int v) const {
        if (!is_built_) throw std::logic_error("Структура не ініціалізована. Викличте build().");
        if (is_ancestor(u, v)) return u;
        if (is_ancestor(v, u)) return v;

        for (int k = logn_ - 1; k >= 0; --k) {
            if (!is_ancestor(up_[u][k], v)) {
                u = up_[u][k];
            }
        }
        return up_[u][0];
    }

    [[nodiscard]] int kth_ancestor(int u, int k) const {
        if (!is_built_) throw std::logic_error("Структура не ініціалізована.");
        if (k > depth_[u]) return 0;

        for (int i = 0; i < logn_; ++i) {
            if ((k >> i) & 1) {
                u = up_[u][i];
            }
        }
        return u;
    }

    [[nodiscard]] int distance_edges(int u, int v) const {
        int lca_node = query(u, v);
        return depth_[u] + depth_[v] - 2 * depth_[lca_node];
    }

    [[nodiscard]] WeightType weighted_distance(int u, int v) const {
        int lca_node = query(u, v);
        return dist_root_[u] + dist_root_[v] - 2 * dist_root_[lca_node];
    }

    [[nodiscard]] int depth(int u) const {
        return depth_[u];
    }
};

} // namespace math::graph
