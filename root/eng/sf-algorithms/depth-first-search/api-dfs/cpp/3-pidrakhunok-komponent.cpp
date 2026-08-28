// C++20 реалізація розмітки компонент
#include <vector>

class ComponentLabelerVisitor : public algo::default_dfs_visitor {
private:
    int current_component_{-1};
    std::vector<int> component_ids_;

public:
    explicit ComponentLabelerVisitor(std::size_t num_vertices)
        : component_ids_(num_vertices, -1) {}

    void start_vertex(int u) noexcept {
        ++current_component_;
    }

    void discover_vertex(int u, int /*d_time*/) noexcept {
        component_ids_[u] = current_component_;
    }

    [[nodiscard]] int num_components() const noexcept {
        return current_component_ + 1;
    }

    [[nodiscard]] const std::vector<int>& component_ids() const noexcept {
        return component_ids_;
    }
};
