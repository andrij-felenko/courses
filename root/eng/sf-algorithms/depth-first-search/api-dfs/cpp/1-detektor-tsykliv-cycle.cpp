// C++20 реалізація детектора циклів
#include <iostream>

struct CycleDetectorVisitor : public algo::default_dfs_visitor {
    bool has_cycle{false};
    int cycle_src{-1};
    int cycle_dst{-1};

    void back_edge(int u, int v) noexcept {
        has_cycle = true;
        cycle_src = u;
        cycle_dst = v;
    }
};
