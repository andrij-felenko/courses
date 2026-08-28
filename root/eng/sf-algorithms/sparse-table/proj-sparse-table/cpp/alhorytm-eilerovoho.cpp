#include <vector>
#include <algorithm>
#include <cstddef>
#include <cstdint>

struct EulerEntry {
    std::size_t node{0};
    int32_t depth{0};

    bool operator<(const EulerEntry& other) const noexcept {
        return depth < other.depth;
    }
};

class TreeLCA {
public:
    explicit TreeLCA(const std::vector<std::vector<std::size_t>>& adj, std::size_t root = 0) {
        std::size_t n = adj.size();
        if (n == 0) return;

        first_occ_.resize(n, 0);
        tour_.reserve(2 * n);

        auto dfs = [&](auto self, std::size_t u, std::size_t p, int32_t d) -> void {
            first_occ_[u] = tour_.size();
            tour_.push_back({u, d});

            for (std::size_t v : adj[u]) {
                if (v != p) {
                    self(self, v, u, d + 1);
                    tour_.push_back({u, d});
                }
            }
        };

        dfs(dfs, root, root, 0);
        st_ = std::make_unique<SparseTable<EulerEntry>>(tour_);
    }

    [[nodiscard]] std::size_t query(std::size_t u, std::size_t v) const noexcept {
        std::size_t l = first_occ_[u];
        std::size_t r = first_occ_[v];
        if (l > r) std::swap(l, r);

        auto res = st_->query(l, r);
        return res ? res->node : 0;
    }

private:
    std::vector<std::size_t> first_occ_;
    std::vector<EulerEntry> tour_;
    std::unique_ptr<SparseTable<EulerEntry>> st_;
};
