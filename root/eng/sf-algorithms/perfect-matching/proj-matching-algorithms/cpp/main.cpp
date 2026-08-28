#include <iostream>
#include <vector>
#include <queue>
#include <numeric>
#include <algorithm>
#include <utility>

class EdmondsBlossomSolver {
public:
    explicit EdmondsBlossomSolver(int num_vertices)
        : n_(num_vertices), adj_(num_vertices), match_(num_vertices, -1) {}

    void add_edge(int u, int v) {
        adj_[u].push_back(v);
        adj_[v].push_back(u);
    }

    int compute_max_matching() {
        std::fill(match_.begin(), match_.end(), -1);
        int matching_size = 0;

        for (int i = 0; i < n_; ++i) {
            if (match_[i] == -1) {
                int end_vertex = find_augmenting_path(i);
                if (end_vertex != -1) {
                    augment_path(end_vertex);
                    matching_size++;
                }
            }
        }
        return matching_size;
    }

    [[nodiscard]] bool is_perfect_matching() const {
        if (n_ % 2 != 0) return false;
        // Створення копії для обчислення без модифікації стану об'єкта
        EdmondsBlossomSolver solver_copy = *this;
        return solver_copy.compute_max_matching() == (n_ / 2);
    }

    [[nodiscard]] std::vector<std::pair<int, int>> get_matching_edges() const {
        std::vector<std::pair<int, int>> edges;
        for (int i = 0; i < n_; ++i) {
            if (match_[i] > i) {
                edges.emplace_back(i, match_[i]);
            }
        }
        return edges;
    }

private:
    int n_;
    std::vector<std::vector<int>> adj_;
    std::vector<int> match_;
    std::vector<int> parent_;

    int find_lca(int u, int v, const std::vector<int>& base) {
        std::vector<bool> in_path(n_, false);

        while (true) {
            u = base[u];
            in_path[u] = true;
            if (match_[u] == -1) break;
            u = parent_[match_[u]];
        }

        while (true) {
            v = base[v];
            if (in_path[v]) return v;
            v = parent_[match_[v]];
        }
    }

    void mark_blossom(int u, int v, int b, std::vector<int>& base, std::vector<bool>& in_blossom) {
        while (base[u] != b) {
            in_blossom[base[u]] = true;
            in_blossom[base[v]] = true;
            parent_[u] = v;
            v = match_[u];
            u = parent_[v];
        }
    }

    int find_augmenting_path(int root) {
        std::vector<int> state(n_, -1);
        std::vector<int> base(n_);
        std::iota(base.begin(), base.end(), 0);
        parent_.assign(n_, -1);

        std::queue<int> q;
        q.push(root);
        state[root] = 0;

        while (!q.empty()) {
            int u = q.front();
            q.pop();

            for (int v : adj_[u]) {
                if (base[u] == base[v] || match_[u] == v) continue;

                if (state[v] == -1) {
                    parent_[v] = u;
                    state[v] = 1;

                    if (match_[v] == -1) return v;

                    int w = match_[v];
                    state[w] = 0;
                    parent_[w] = v;
                    q.push(w);
                } else if (state[base[v]] == 0) {
                    int b = find_lca(u, v, base);
                    std::vector<bool> in_blossom(n_, false);

                    mark_blossom(u, v, b, base, in_blossom);
                    mark_blossom(v, u, b, base, in_blossom);

                    for (int i = 0; i < n_; ++i) {
                        if (in_blossom[base[i]]) {
                            base[i] = b;
                            if (state[i] == 1) {
                                state[i] = 0;
                                q.push(i);
                            }
                        }
                    }
                }
            }
        }
        return -1;
    }

    void augment_path(int v) {
        while (v != -1) {
            int pv = parent_[v];
            int ppv = match_[pv];
            match_[v] = pv;
            match_[pv] = v;
            v = ppv;
        }
    }
};
