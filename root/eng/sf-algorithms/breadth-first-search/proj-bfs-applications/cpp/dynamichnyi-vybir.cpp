#include <vector>
#include <queue>

int bidirectional_bfs_cpp(const std::vector<std::vector<int>>& adj, int start, int target) {
    if (start == target) return 0;
    int n = adj.size();

    std::vector<int> dist_f(n, -1), dist_b(n, -1);
    std::queue<int> q_f, q_b;

    dist_f[start] = 0; q_f.push(start);
    dist_b[target] = 0; q_b.push(target);

    while (!q_f.empty() && !q_b.empty()) {
        int u_f = q_f.front(); q_f.pop();
        for (int v : adj[u_f]) {
            if (dist_b[v] != -1) return dist_f[u_f] + 1 + dist_b[v];
            if (dist_f[v] == -1) {
                dist_f[v] = dist_f[u_f] + 1;
                q_f.push(v);
            }
        }

        int u_b = q_b.front(); q_b.pop();
        for (int v : adj[u_b]) {
            if (dist_f[v] != -1) return dist_b[u_b] + 1 + dist_f[v];
            if (dist_b[v] == -1) {
                dist_b[v] = dist_b[u_b] + 1;
                q_b.push(v);
            }
        }
    }
    return -1;
}
