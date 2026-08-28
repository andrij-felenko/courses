#include <vector>
#include <stack>
#include <algorithm>

std::vector<std::vector<int>> compute_scc_iterative_cpp(int n, const std::vector<std::vector<int>>& adj) {
    std::vector<int> tin(n, 0), low(n, 0);
    std::vector<bool> in_stack(n, false);
    std::stack<int> scc_stack;
    std::vector<std::vector<int>> result;
    int timer = 0;

    struct DfsFrame {
        int u;
        size_t edge_idx;
    };
    std::stack<DfsFrame> dfs_stack;

    for (int start = 0; start < n; ++start) {
        if (tin[start] != 0) continue;

        dfs_stack.push({start, 0});
        tin[start] = low[start] = ++timer;
        scc_stack.push(start);
        in_stack[start] = true;

        while (!dfs_stack.empty()) {
            auto& [u, idx] = dfs_stack.top();

            if (idx < adj[u].size()) {
                int v = adj[u][idx++];
                if (tin[v] == 0) {
                    tin[v] = low[v] = ++timer;
                    scc_stack.push(v);
                    in_stack[v] = true;
                    dfs_stack.push({v, 0});
                } else if (in_stack[v]) {
                    low[u] = std::min(low[u], tin[v]);
                }
            } else {
                dfs_stack.pop();
                if (!dfs_stack.empty()) {
                    int parent = dfs_stack.top().u;
                    low[parent] = std::min(low[parent], low[u]);
                }

                if (low[u] == tin[u]) {
                    std::vector<int> current_scc;
                    while (true) {
                        int v = scc_stack.top();
                        scc_stack.pop();
                        in_stack[v] = false;
                        current_scc.push_back(v);
                        if (u == v) break;
                    }
                    result.push_back(std::move(current_scc));
                }
            }
        }
    }
    return result;
}
