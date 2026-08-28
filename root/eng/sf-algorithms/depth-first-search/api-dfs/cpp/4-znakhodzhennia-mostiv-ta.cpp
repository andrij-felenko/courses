// C++20 реалізація знаходження мостів
#include <vector>
#include <algorithm>

class BridgeFinderVisitor : public algo::default_dfs_visitor {
private:
    std::vector<int> d_;
    std::vector<int> low_;
    std::vector<std::pair<int, int>> bridges_;

public:
    explicit BridgeFinderVisitor(std::size_t n) : d_(n, 0), low_(n, 0) {}

    void discover_vertex(int u, int time) noexcept {
        d_[u] = time;
        low_[u] = time;
    }

    void back_edge(int u, int v) noexcept {
        low_[u] = std::min(low_[u], d_[v]);
    }

    void finish_edge(int u, int v) noexcept {
        low_[u] = std::min(low_[u], low_[v]);
        if (low_[v] > d_[u]) {
            bridges_.push_back({u, v});
        }
    }

    [[nodiscard]] const std::vector<std::pair<int, int>>& bridges() const noexcept {
        return bridges_;
    }
};
