#include <iostream>
#include <vector>
#include <utility>

struct BipartiteMatchingSystem {
    int n_left;
    int n_right;
    DinicSolver<int64_t> solver;

    BipartiteMatchingSystem(int l, int r)
        : n_left(l), n_right(r), solver(l + r + 2) {}

    void add_edge(int u, int v) {
        solver.add_edge(u + 1, n_left + 1 + v, 1);
    }

    int compute_matching() {
        int s = 0;
        int t = n_left + n_right + 1;

        for (int i = 0; i < n_left; ++i) {
            solver.add_edge(s, i + 1, 1);
        }
        for (int j = 0; j < n_right; ++j) {
            solver.add_edge(n_left + 1 + j, t, 1);
        }

        return static_cast<int>(solver.max_flow(s, t));
    }

    std::pair<std::vector<int>, std::vector<int>> get_vertex_cover() {
        int s = 0;
        std::vector<bool> in_s = solver.min_cut(s);
        std::vector<int> cover_left, cover_right;

        for (int i = 0; i < n_left; ++i) {
            if (!in_s[i + 1]) cover_left.push_back(i);
        }
        for (int j = 0; j < n_right; ++j) {
            if (in_s[n_left + 1 + j]) cover_right.push_back(j);
        }

        return {cover_left, cover_right};
    }
};
