#include <iostream>
#include <vector>
#include <queue>
#include <numeric>
#include <algorithm>
#include <span>

class BlossomMatcher {
public:
    explicit BlossomMatcher(int num_vertices)
        : n_(num_vertices), adj_(num_vertices), match_(num_vertices, -1) {}

    void add_edge(int u, int v) {
        if (u >= 0 && u < n_ && v >= 0 && v < n_ && u != v) {
            adj_[u].push_back(v);
            adj_[v].push_back(u);
        }
    }

    int solve() {
        int matching_size = 0;
        std::vector<int> parent(n_, -1);
        std::vector<int> base(n_);

        for (int i = 0; i < n_; ++i) {
            if (match_[i] != -1) {
                continue;
            }

            int target = find_augmenting_path(i, parent, base);
            if (target != -1) {
                augment_path(target, parent);
                matching_size++;
            }
        }

        return matching_size;
    }

    [[nodiscard]] std::span<const int> matching() const noexcept {
        return match_;
    }

    [[nodiscard]] int partner_of(int u) const noexcept {
        return (u >= 0 && u < n_) ? match_[u] : -1;
    }

private:
    int n_;
    std::vector<std::vector<int>> adj_;
    std::vector<int> match_;

    int dsu_find(std::vector<int>& base, int u) const {
        if (base[u] == u) {
            return u;
        }
        return base[u] = dsu_find(base, base[u]);
    }

    void dsu_union(std::vector<int>& base, int u, int v) const {
        int root_u = dsu_find(base, u);
        int root_v = dsu_find(base, v);
        if (root_u != root_v) {
            base[root_u] = root_v;
        }
    }

    int find_lca(std::vector<int>& base, const std::vector<int>& parent, int u, int v) const {
        std::vector<bool> used(n_, false);

        while (true) {
            u = dsu_find(base, u);
            used[u] = true;
            if (match_[u] == -1) {
                break;
            }
            u = parent[match_[u]];
        }

        while (true) {
            v = dsu_find(base, v);
            if (used[v]) {
                return v;
            }
            if (match_[v] == -1) {
                break;
            }
            v = parent[match_[v]];
        }

        return -1;
    }

    void contract_blossom_arm(std::queue<int>& q, std::vector<bool>& in_queue,
                              std::vector<int>& base, std::vector<int>& parent,
                              int u, int v, int lca) const {
        while (dsu_find(base, u) != lca) {
            parent[u] = v;
            v = match_[u];
            if (!in_queue[v]) {
                in_queue[v] = true;
                q.push(v);
            }
            dsu_union(base, u, lca);
            dsu_union(base, v, lca);
            u = parent[v];
        }
    }

    int find_augmenting_path(int root, std::vector<int>& parent, std::vector<int>& base) const {
        std::fill(parent.begin(), parent.end(), -1);
        std::iota(base.begin(), base.end(), 0);

        std::vector<bool> in_queue(n_, false);
        std::queue<int> q;

        q.push(root);
        in_queue[root] = true;

        while (!q.empty()) {
            int u = q.front();
            q.pop();
            in_queue[u] = false;

            for (int v : adj_[u]) {
                if (dsu_find(base, u) == dsu_find(base, v) || match_[u] == v) {
                    continue;
                }

                if (v == root || (match_[v] != -1 && parent[match_[v]] != -1)) {
                    int lca = find_lca(base, parent, u, v);
                    if (lca != -1) {
                        contract_blossom_arm(q, in_queue, base, parent, u, v, lca);
                        contract_blossom_arm(q, in_queue, base, parent, v, u, lca);
                    }
                } else if (parent[v] == -1) {
                    parent[v] = u;
                    if (match_[v] == -1) {
                        return v;
                    }
                    int w = match_[v];
                    parent[w] = v;
                    if (!in_queue[w]) {
                        in_queue[w] = true;
                        q.push(w);
                    }
                }
            }
        }

        return -1;
    }

    void augment_path(int target, const std::vector<int>& parent) {
        int curr = target;
        while (curr != -1) {
            int p = parent[curr];
            int next_node = (p != -1) ? match_[p] : -1;
            match_[curr] = p;
            if (p != -1) {
                match_[p] = curr;
            }
            curr = next_node;
        }
    }
};
