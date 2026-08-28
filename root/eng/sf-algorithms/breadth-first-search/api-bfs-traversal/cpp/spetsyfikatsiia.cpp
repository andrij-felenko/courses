#include <vector>
#include <queue>
#include <concepts>

// Шаблонний порожній базовий відвідувач
struct default_bfs_visitor {
    void initialize_vertex(int /*u*/) {}
    void start_vertex(int /*u*/) {}
    void discover_vertex(int /*u*/) {}
    void examine_vertex(int /*u*/) {}
    void examine_edge(int /*u*/, int /*v*/) {}
    void tree_edge(int /*u*/, int /*v*/) {}
    void non_tree_edge(int /*u*/, int /*v*/) {}
    void finish_vertex(int /*u*/) {}
};

// Універсальний рушій BFS мовою C++
template <typename Visitor>
void breadth_first_search_generic(
    const std::vector<std::vector<int>>& adj,
    int start_node,
    Visitor visitor) 
{
    std::size_t n = adj.size();
    std::vector<bool> visited(n, false);
    std::queue<int> q;

    for (std::size_t i = 0; i < n; ++i) {
        visitor.initialize_vertex(static_cast<int>(i));
    }

    visitor.start_vertex(start_node);
    visited[start_node] = true;
    visitor.discover_vertex(start_node);
    q.push(start_node);

    while (!q.empty()) {
        int u = q.front();
        q.pop();

        visitor.examine_vertex(u);

        for (int v : adj[u]) {
            visitor.examine_edge(u, v);
            if (!visited[v]) {
                visited[v] = true;
                visitor.tree_edge(u, v);
                visitor.discover_vertex(v);
                q.push(v);
            } else {
                visitor.non_tree_edge(u, v);
            }
        }

        visitor.finish_vertex(u);
    }
}
