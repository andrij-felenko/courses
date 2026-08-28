#include <vector>
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <stdexcept>

class BinaryLiftingLCA {
private:
    int n_;
    int logn_;
    std::vector<int> depth_;
    std::vector<std::vector<int>> up_;
    std::vector<std::vector<int>> adj_;

    void dfs(int u, int p, int d) {
        depth_[u] = d;
        up_[u][0] = p;

        for (int k = 1; k < logn_; ++k) {
            up_[u][k] = up_[up_[u][k - 1]][k - 1];
        }

        for (int v : adj_[u]) {
            if (v != p) {
                dfs(v, u, d + 1);
            }
        }
    }

public:
    explicit BinaryLiftingLCA(int n)
        : n_(n), logn_(std::ceil(std::log2(n + 1)) + 1),
          depth_(n + 1, 0), up_(n + 1, std::vector<int>(logn_, 0)), adj_(n + 1) {}

    void add_edge(int u, int v) {
        adj_[u].push_back(v);
        adj_[v].push_back(u);
    }

    void build(int root = 1) {
        dfs(root, root, 0);
    }

    [[nodiscard]] int query(int u, int v) const {
        if (depth_[u] < depth_[v]) {
            std::swap(u, v);
        }

        int diff = depth_[u] - depth_[v];
        for (int k = logn_ - 1; k >= 0; --k) {
            if ((diff >> k) & 1) {
                u = up_[u][k];
            }
        }

        if (u == v) return u;

        for (int k = logn_ - 1; k >= 0; --k) {
            if (up_[u][k] != up_[v][k]) {
                u = up_[u][k];
                v = up_[v][k];
            }
        }

        return up_[u][0];
    }

    [[nodiscard]] int distance(int u, int v) const {
        int l = query(u, v);
        return depth_[u] + depth_[v] - 2 * depth_[l];
    }
};
