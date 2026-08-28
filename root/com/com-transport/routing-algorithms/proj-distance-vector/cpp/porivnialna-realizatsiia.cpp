struct GraphLink {
    int to;
    int cost;
};

void run_dijkstra_spt(int source, int total_nodes, const std::vector<std::vector<GraphLink>>& adj) {
    std::vector<int> dist(total_nodes, INF);
    std::vector<int> parent(total_nodes, -1);
    using PII = std::pair<int, int>; // (cost, node)
    std::priority_queue<PII, std::vector<PII>, std::greater<PII>> pq;

    dist[source] = 0;
    pq.push({0, source});

    while (!pq.empty()) {
        auto [d, u] = pq.top();
        pq.pop();

        if (d > dist[u]) continue;

        for (const auto& edge : adj[u]) {
            if (dist[u] + edge.cost < dist[edge.to]) {
                dist[edge.to] = dist[u] + edge.cost;
                parent[edge.to] = u;
                pq.push({dist[edge.to], edge.to});
            }
        }
    }
}
