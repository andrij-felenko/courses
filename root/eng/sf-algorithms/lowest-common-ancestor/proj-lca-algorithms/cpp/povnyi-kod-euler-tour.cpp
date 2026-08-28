#include <vector>
#include <algorithm>
#include <cmath>

class EulerTourRMQLCA {
private:
    int n_;
    std::vector<std::vector<int>> adj_;
    std::vector<int> euler_;
    std::vector<int> depth_nodes_;
    std::vector<int> first_;
    std::vector<std::vector<int>> st_;
    std::vector<int> log_table_;

    void dfs(int u, int p, int d) {
        first_[u] = static_cast<int>(euler_.size());
        euler_.push_back(u);
        depth_nodes_.push_back(d);

        for (int v : adj_[u]) {
            if (v != p) {
                dfs(v, u, d + 1);
                euler_.push_back(u);
                depth_nodes_.push_back(d);
            }
        }
    }

public:
    explicit EulerTourRMQLCA(int n)
        : n_(n), adj_(n + 1), first_(n + 1, 0) {}

    void add_edge(int u, int v) {
        adj_[u].push_back(v);
        adj_[v].push_back(u);
    }

    void build(int root = 1) {
        dfs(root, 0, 0);

        int m = static_cast<int>(euler_.size());
        log_table_.assign(m + 1, 0);
        for (int i = 2; i <= m; ++i) {
            log_table_[i] = log_table_[i / 2] + 1;
        }

        int max_log = log_table_[m] + 1;
        st_.assign(m, std::vector<int>(max_log));

        for (int i = 0; i < m; ++i) {
            st_[i][0] = euler_[i];
        }

        auto min_node = [this](int u_node, int v_node) {
            return (depth_nodes_[first_[u_node]] < depth_nodes_[first_[v_node]]) ? u_node : v_node;
        };

        for (int j = 1; j < max_log; ++j) {
            for (int i = 0; i + (1 << j) <= m; ++i) {
                st_[i][j] = min_node(st_[i][j - 1], st_[i + (1 << (j - 1))][j - 1]);
            }
        }
    }

    [[nodiscard]] int query(int u, int v) const {
        int l = first_[u];
        int r = first_[v];
        if (l > r) std::swap(l, r);

        int len = r - l + 1;
        int k = log_table_[len];

        int node1 = st_[l][k];
        int node2 = st_[r - (1 << k) + 1][k];

        return (depth_nodes_[first_[node1]] < depth_nodes_[first_[node2]]) ? node1 : node2;
    }
};
