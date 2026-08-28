#include <iostream>
#include <vector>
#include <queue>
#include <span>
#include <cstdint>

/* 1. Пошук у ширину (BFS) на матриці суміжності: складність O(V²) */
class MatrixGraph {
public:
    explicit MatrixGraph(uint32_t num_vertices)
        : num_vertices_(num_vertices), matrix_(static_cast<size_t>(num_vertices) * num_vertices, 0) {}

    void add_edge(uint32_t u, uint32_t v) {
        if (u < num_vertices_ && v < num_vertices_) {
            matrix_[static_cast<size_t>(u) * num_vertices_ + v] = 1;
        }
    }

    void bfs(uint32_t start_node) const {
        if (start_node >= num_vertices_) return;

        std::vector<bool> visited(num_vertices_, false);
        std::queue<uint32_t> q;

        visited[start_node] = true;
        q.push(start_node);

        while (!q.empty()) {
            uint32_t u = q.front();
            q.pop();

            // Сканування всього рядка довжиною V
            size_t row_offset = static_cast<size_t>(u) * num_vertices_;
            for (uint32_t v = 0; v < num_vertices_; ++v) {
                if (matrix_[row_offset + v] && !visited[v]) {
                    visited[v] = true;
                    q.push(v);
                }
            }
        }
    }

private:
    uint32_t num_vertices_;
    std::vector<uint8_t> matrix_;
};

/* 2. Пошук у ширину (BFS) на списках суміжності: складність O(V + E) */
class ListGraph {
public:
    explicit ListGraph(uint32_t num_vertices)
        : adj_(num_vertices) {}

    void add_edge(uint32_t u, uint32_t v) {
        if (u < adj_.size()) {
            adj_[u].push_back(v);
        }
    }

    void bfs(uint32_t start_node) const {
        if (start_node >= adj_.size()) return;

        std::vector<bool> visited(adj_.size(), false);
        std::queue<uint32_t> q;

        visited[start_node] = true;
        q.push(start_node);

        while (!q.empty()) {
            uint32_t u = q.front();
            q.pop();

            // Сканування лише існуючих сусідів (deg(u))
            for (uint32_t v : adj_[u]) {
                if (!visited[v]) {
                    visited[v] = true;
                    q.push(v);
                }
            }
        }
    }

private:
    std::vector<std::vector<uint32_t>> adj_;
};
