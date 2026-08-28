#include <vector>

class ComponentLabelerVisitor : public default_bfs_visitor {
private:
    int current_component_;
    std::vector<int>& component_map_;

public:
    ComponentLabelerVisitor(int comp_id, std::vector<int>& comp_map)
        : current_component_(comp_id), component_map_(comp_map) {}

    void discover_vertex(int u) {
        component_map_[u] = current_component_;
    }
};

std::vector<int> compute_components_cpp(const std::vector<std::vector<int>>& graph) {
    std::size_t n = graph.size();
    std::vector<int> component_map(n, -1);
    int comp_id = 0;

    for (std::size_t i = 0; i < n; ++i) {
        if (component_map[i] == -1) {
            ComponentLabelerVisitor visitor(comp_id++, component_map);
            breadth_first_search_generic(graph, static_cast<int>(i), visitor);
        }
    }

    return component_map;
}
