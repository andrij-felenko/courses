#include <vector>
#include <queue>

bool is_bipartite_cpp(const std::vector<std::vector<int>>& adj) {
    int n = adj.size();
    std::vector<int> color(n, 0);

    for (int start = 0; start < n; ++start) {
        if (color[start] != 0) continue;

        std::queue<int> q;
        color[start] = 1;
        q.push(start);

        while (!q.empty()) {
            int u = q.front();
            q.pop();

            for (int v : adj[u]) {
                if (color[v] == 0) {
                    color[v] = 3 - color[u];
                    q.push(v);
                } else if (color[v] == color[u]) {
                    return false;
                }
            }
        }
    }
    return true;
}
