#include <iostream>
#include <vector>
#include <stack>
#include <algorithm>
#include <span >

class TarjanSCCSolver {
public:
    explicit TarjanSCCSolver(int vertices)
        : adj_(vertices), tin_(vertices, 0), low_(vertices, 0), in_stack_(vertices, false) {}

    void add_edge(int u, int v) {
        adj_[u].push_back(v);
    }

    std::vector<std::vector<int>> compute_scc() {
        sccs_.clear();
        timer_ = 0;
        std::fill(tin_.begin(), tin_.end(), 0);
        std::fill(low_.begin(), low_.end(), 0);
        std::fill(in_stack_.begin(), in_stack_.end(), false);

        for (int i = 0; i < static_cast<int>(adj_.size()); ++i) {
            if (tin_[i] == 0) {
                dfs(i);
            }
        }
        return sccs_;
    }

private:
    std::vector<std::vector<int>> adj_;
    std::vector<int> tin_;
    std::vector<int> low_;
    std::vector<bool> in_stack_;
    std::stack<int> st_;
    std::vector<std::vector<int>> sccs_;
    int timer_{0};

    void dfs(int u) {
        tin_[u] = low_[u] = ++timer_;
        st_.push(u);
        in_stack_[u] = true;

        for (int v : adj_[u]) {
            if (tin_[v] == 0) {
                dfs(v);
                low_[u] = std::min(low_[u], low_[v]);
            } else if (in_stack_[v]) {
                low_[u] = std::min(low_[u], tin_[v]);
            }
        }

        if (low_[u] == tin_[u]) {
            std::vector<int> current_scc;
            while (true) {
                int v = st_.top();
                st_.pop();
                in_stack_[v] = false;
                current_scc.push_back(v);
                if (u == v) break;
            }
            sccs_.push_back(std::move(current_scc));
        }
    }
};
