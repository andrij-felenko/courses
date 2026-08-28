#include <vector>
#include <queue>
#include <limits>
#include <cstdint>
#include <algorithm>

template <typename FlowType = int64_t>
class IterativeDinic {
public:
    struct Edge {
        int to;
        int rev;
        FlowType cap;
        FlowType flow;
    };

    explicit IterativeDinic(int vertices)
        : n(vertices), adj(vertices), level(vertices), ptr(vertices), path(vertices) {}

    void add_edge(int u, int v, FlowType cap, FlowType rev_cap = 0) {
        if (u == v) return;
        Edge fwd{v, static_cast<int>(adj[v].size()), cap, 0};
        Edge bwd{u, static_cast<int>(adj[u].size()), rev_cap, 0};
        adj[u].push_back(fwd);
        adj[v].push_back(bwd);
    }

    FlowType max_flow(int s, int t) {
        FlowType total_flow = 0;
        while (bfs(s, t)) {
            std::fill(ptr.begin(), ptr.end(), 0);
            total_flow += push_blocking_flow(s, t);
        }
        return total_flow;
    }

private:
    int n;
    std::vector<std::vector<Edge>> adj;
    std::vector<int> level;
    std::vector<size_t> ptr;
    std::vector<int> path; // Явний стек для вершин шляху

    bool bfs(int s, int t) {
        std::fill(level.begin(), level.end(), -1);
        std::queue<int> q;
        level[s] = 0;
        q.push(s);

        while (!q.empty()) {
            int u = q.front();
            q.pop();
            for (const auto& e : adj[u]) {
                if (e.cap - e.flow > 0 && level[e.to] == -1) {
                    level[e.to] = level[u] + 1;
                    q.push(e.to);
                }
            }
        }
        return level[t] != -1;
    }

    FlowType push_blocking_flow(int s, int t) {
        FlowType phase_flow = 0;
        int path_len = 0;
        path[path_len++] = s;

        while (path_len > 0) {
            int u = path[path_len - 1];

            if (u == t) {
                // Знайдено шлях від s до t: обчислюємо пляшкове горло
                FlowType pushed = std::numeric_limits<FlowType>::max();
                int bottleneck_idx = -1;

                for (int i = 0; i < path_len - 1; ++i) {
                    int curr = path[i];
                    const auto& e = adj[curr][ptr[curr]];
                    if (e.cap - e.flow < pushed) {
                        pushed = e.cap - e.flow;
                        bottleneck_idx = i;
                    }
                }

                // Оновлюємо потоки вздовж знайденого шляху
                for (int i = 0; i < path_len - 1; ++i) {
                    int curr = path[i];
                    auto& e = adj[curr][ptr[curr]];
                    e.flow += pushed;
                    adj[e.to][e.rev].flow -= pushed;
                }

                phase_flow += pushed;
                // Відкочуємося до вершини перед першим насиченим ребром
                path_len = bottleneck_idx + 1;
                continue;
            }

            // Шукаємо наступне допустиме ребро з вершини u
            bool advanced = false;
            while (ptr[u] < adj[u].size()) {
                const auto& e = adj[u][ptr[u]];
                if (level[u] + 1 == level[e.to] && e.cap - e.flow > 0) {
                    path[path_len++] = e.to;
                    advanced = true;
                    break;
                }
                ++ptr[u];
            }

            // Якщо вихідних допустимих ребер немає — відступаємо назад (Retreat)
            if (!advanced) {
                --path_len;
                if (path_len > 0) {
                    int prev = path[path_len - 1];
                    ++ptr[prev]; // Пропускаємо використане ребро
                }
            }
        }
        return phase_flow;
    }
};
