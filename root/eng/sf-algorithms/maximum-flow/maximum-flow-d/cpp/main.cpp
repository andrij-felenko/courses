#include <iostream>
#include <vector>
#include <queue>
#include <limits>
#include <cstdint>
#include <algorithm>

template <typename FlowType = int64_t>
class EdmondsKarp {
public:
    struct Edge {
        int to;
        int rev;
        FlowType cap;
        FlowType flow;
    };

    explicit EdmondsKarp(int vertices)
        : n(vertices), adj(vertices) {}

    void add_edge(int from, int to, FlowType cap, FlowType rev_cap = 0) {
        if (from == to || from < 0 || to < 0 || from >= n || to >= n) return;
        Edge forward_edge{to, static_cast<int>(adj[to].size()), cap, 0};
        Edge backward_edge{from, static_cast<int>(adj[from].size()), rev_cap, 0};
        adj[from].push_back(forward_edge);
        adj[to].push_back(backward_edge);
    }

    FlowType max_flow(int s, int t) {
        if (s == t || s < 0 || t < 0 || s >= n || t >= n) return 0;
        FlowType total_flow = 0;

        std::vector<int> parent_node(n, -1);
        std::vector<int> parent_edge(n, -1);

        while (bfs(s, t, parent_node, parent_edge)) {
            FlowType push_delta = std::numeric_limits<FlowType>::max();

            // 1. Пошук пляшкового горла вздовж знайденого шляху
            for (int curr = t; curr != s; curr = parent_node[curr]) {
                int p = parent_node[curr];
                int edge_idx = parent_edge[curr];
                const Edge& e = adj[p][edge_idx];
                push_delta = std::min(push_delta, e.cap - e.flow);
            }

            // 2. Аугментація потоку
            for (int curr = t; curr != s; curr = parent_node[curr]) {
                int p = parent_node[curr];
                int edge_idx = parent_edge[curr];
                Edge& forward_e = adj[p][edge_idx];
                Edge& backward_e = adj[curr][forward_e.rev];

                forward_e.flow += push_delta;
                backward_e.flow -= push_delta;
            }

            total_flow += push_delta;
        }

        return total_flow;
    }

    std::vector<bool> min_cut(int s) const {
        std::vector<bool> visited(n, false);
        std::queue<int> q;
        q.push(s);
        visited[s] = true;

        while (!q.empty()) {
            int u = q.front();
            q.pop();

            for (const auto& edge : adj[u]) {
                if (edge.cap - edge.flow > 0 && !visited[edge.to]) {
                    visited[edge.to] = true;
                    q.push(edge.to);
                }
            }
        }
        return visited;
    }

private:
    int n;
    std::vector<std::vector<Edge>> adj;

    bool bfs(int s, int t, std::vector<int>& parent_node, std::vector<int>& parent_edge) {
        std::fill(parent_node.begin(), parent_node.end(), -1);
        std::fill(parent_edge.begin(), parent_edge.end(), -1);

        std::queue<int> q;
        q.push(s);
        parent_node[s] = s;

        while (!q.empty()) {
            int u = q.front();
            q.pop();

            if (u == t) break;

            for (size_t i = 0; i < adj[u].size(); ++i) {
                const Edge& edge = adj[u][i];
                if (edge.cap - edge.flow > 0 && parent_node[edge.to] == -1) {
                    parent_node[edge.to] = u;
                    parent_edge[edge.to] = static_cast<int>(i);
                    q.push(edge.to);
                }
            }
        }

        return parent_node[t] != -1;
    }
};
