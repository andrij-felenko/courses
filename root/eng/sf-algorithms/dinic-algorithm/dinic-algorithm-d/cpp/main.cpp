#include <iostream>
#include <vector>
#include <queue>
#include <limits>
#include <cstdint>
#include <algorithm>

template <typename FlowType = int64_t>
class Dinic {
public:
    struct Edge {
        int to;
        int rev;
        FlowType cap;
        FlowType flow;
    };

    explicit Dinic(int vertices)
        : n(vertices), adj(vertices), level(vertices), ptr(vertices) {}

    void add_edge(int from, int to, FlowType cap, FlowType rev_cap = 0) {
        if (from == to) return;
        Edge forward_edge{to, static_cast<int>(adj[to].size()), cap, 0};
        Edge backward_edge{from, static_cast<int>(adj[from].size()), rev_cap, 0};
        adj[from].push_back(forward_edge);
        adj[to].push_back(backward_edge);
    }

    FlowType max_flow(int s, int t) {
        FlowType total_flow = 0;
        const FlowType flow_limit = std::numeric_limits<FlowType>::max();

        while (bfs(s, t)) {
            std::fill(ptr.begin(), ptr.end(), 0);
            while (FlowType pushed = dfs(s, t, flow_limit)) {
                total_flow += pushed;
            }
        }
        return total_flow;
    }

    std::vector<bool> min_cut(int s) {
        std::vector<bool> reachable(n, false);
        std::queue<int> q;
        q.push(s);
        reachable[s] = true;

        while (!q.empty()) {
            int u = q.front();
            q.pop();
            for (const auto& edge : adj[u]) {
                if (edge.cap - edge.flow > 0 && !reachable[edge.to]) {
                    reachable[edge.to] = true;
                    q.push(edge.to);
                }
            }
        }
        return reachable;
    }

private:
    int n;
    std::vector<std::vector<Edge>> adj;
    std::vector<int> level;
    std::vector<size_t> ptr;

    bool bfs(int s, int t) {
        std::fill(level.begin(), level.end(), -1);
        std::queue<int> q;
        level[s] = 0;
        q.push(s);

        while (!q.empty()) {
            int u = q.front();
            q.pop();

            for (const auto& edge : adj[u]) {
                if (edge.cap - edge.flow > 0 && level[edge.to] == -1) {
                    level[edge.to] = level[u] + 1;
                    q.push(edge.to);
                }
            }
        }
        return level[t] != -1;
    }

    FlowType dfs(int u, int t, FlowType pushed) {
        if (pushed == 0 || u == t) return pushed;

        for (size_t& cid = ptr[u]; cid < adj[u].size(); ++cid) {
            Edge& edge = adj[u][cid];
            int trg = edge.to;

            if (level[u] + 1 != level[trg] || edge.cap - edge.flow == 0) {
                continue;
            }

            FlowType tr = dfs(trg, t, std::min(pushed, edge.cap - edge.flow));
            if (tr == 0) continue;

            edge.flow += tr;
            adj[trg][edge.rev].flow -= tr;
            return tr;
        }
        return 0;
    }
};
