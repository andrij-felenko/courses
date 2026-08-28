#include <vector>
#include <optional>
#include <span>
#include <iostream>

class Graph {
public:
    explicit Graph(size_t vertices) 
        : num_vertices_(vertices), adj_matrix_(vertices, std::vector<uint8_t>(vertices, 0)) {}

    void add_edge(size_t u, size_t v) {
        if (u < num_vertices_ && v < num_vertices_) {
            adj_matrix_[u][v] = 1;
            adj_matrix_[v][u] = 1;
        }
    }

    [[nodiscard]] size_t size() const noexcept { return num_vertices_; }
    [[nodiscard]] bool has_edge(size_t u, size_t v) const noexcept { return adj_matrix_[u][v] != 0; }

private:
    size_t num_vertices_;
    std::vector<std::vector<uint8_t>> adj_matrix_;
};

class HamiltonianBacktracker {
public:
    static std::optional<std::vector<size_t>> solve(const Graph& graph) {
        const size_t n = graph.size();
        if (n < 3) return std::nullopt;

        std::vector<size_t> path(n, 0);
        std::vector<bool> visited(n, false);

        visited[0] = true;
        path[0] = 0;

        if (step(graph, 0, 1, visited, path)) {
            return path;
        }
        return std::nullopt;
    }

private:
    static bool step(const Graph& g, size_t curr_v, size_t count, 
                     std::vector<bool>& visited, std::vector<size_t>& path) {
        if (count == g.size()) {
            return g.has_edge(curr_v, path[0]);
        }

        for (size_t next_v = 0; next_v < g.size(); ++next_v) {
            if (g.has_edge(curr_v, next_v) && !visited[next_v]) {
                visited[next_v] = true;
                path[count] = next_v;

                if (step(g, next_v, count + 1, visited, path)) {
                    return true;
                }

                visited[next_v] = false;
            }
        }
        return false;
    }
};
