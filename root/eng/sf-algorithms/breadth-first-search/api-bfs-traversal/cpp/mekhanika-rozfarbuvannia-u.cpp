#include <vector>

class BipartiteCheckerVisitor : public default_bfs_visitor {
private:
    std::vector<int>& color_;
    bool is_bipartite_ = true;

public:
    explicit BipartiteCheckerVisitor(std::vector<int>& color)
        : color_(color) {}

    void start_vertex(int u) {
        if (color_[u] == 0) color_[u] = 1;
    }

    void tree_edge(int u, int v) {
        color_[v] = 3 - color_[u];
    }

    void non_tree_edge(int u, int v) {
        if (color_[u] == color_[v]) {
            is_bipartite_ = false;
        }
    }

    bool is_bipartite() const { return is_bipartite_; }
};

bool check_bipartite_cpp(const std::vector<std::vector<int>>& graph) {
    std::size_t n = graph.size();
    std::vector<int> color(n, 0);
    BipartiteCheckerVisitor visitor(color);

    for (std::size_t i = 0; i < n; ++i) {
        if (color[i] == 0) {
            breadth_first_search_generic(graph, static_cast<int>(i), visitor);
        }
    }

    return visitor.is_bipartite();
}
