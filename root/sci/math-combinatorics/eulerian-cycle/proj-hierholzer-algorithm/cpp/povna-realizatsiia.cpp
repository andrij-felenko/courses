#include <vector>
#include <stack>
#include <optional>
#include <algorithm>
#include <cstddef>
#include <stdexcept>

struct Edge {
    int to;
    int id;
};

class EulerianSolver {
private:
    int num_vertices_;
    int num_edges_{0};
    std::vector<std::vector<Edge>> adj_;
    std::vector<int> in_degree_;
    std::vector<int> out_degree_;

public:
    explicit EulerianSolver(int vertices)
        : num_vertices_(vertices), adj_(vertices), in_degree_(vertices, 0), out_degree_(vertices, 0) {}

    void add_edge(int u, int v) {
        if (u < 0 || u >= num_vertices_ || v < 0 || v >= num_vertices_) {
            throw std::out_of_range("Індекс вершини виходить за межі [0, V-1]");
        }
        adj_[u].push_back({v, num_edges_});
        out_degree_[u]++;
        in_degree_[v]++;
        num_edges_++;
    }

    [[nodiscard]] std::optional<std::vector<int>> find_eulerian_circuit(int start_vertex = 0) const {
        // 1. Перевірка необхідної умови збалансованості степеней
        for (int i = 0; i < num_vertices_; ++i) {
            if (in_degree_[i] != out_degree_[i]) {
                return std::nullopt;
            }
        }

        std::vector<bool> visited_edges(num_edges_, false);
        std::vector<std::size_t> edge_idx(num_vertices_, 0); // Пам'ятаємо індекс першого невідвіданого ребра

        std::stack<int> curr_stack;
        std::vector<int> circuit;
        circuit.reserve(num_edges_ + 1);

        curr_stack.push(start_vertex);

        while (!curr_stack.empty()) {
            int u = curr_stack.top();

            // Знаходимо невідвідане ребро
            while (edge_idx[u] < adj_[u].size() && visited_edges[adj_[u][edge_idx[u]].id]) {
                edge_idx[u]++;
            }

            if (edge_idx[u] < adj_[u].size()) {
                const auto& edge = adj_[u][edge_idx[u]];
                visited_edges[edge.id] = true;
                edge_idx[u]++;
                curr_stack.push(edge.to);
            } else {
                circuit.push_back(u);
                curr_stack.pop();
            }
        }

        // 2. Перевірка зв'язності ребер
        if (circuit.size() != static_cast<std::size_t>(num_edges_ + 1)) {
            return std::nullopt;
        }

        // Реверсуємо вектор результату
        std::reverse(circuit.begin(), circuit.end());
        return circuit;
    }
};
