#include <vector>
#include <optional>
#include <cstddef>
#include <cstdint>

enum class NodeColor : std::uint8_t {
    White,
    Gray,
    Black
};

class DfsBuildGraph {
public:
    explicit DfsBuildGraph(std::size_t node_count)
        : adj_(node_count) {}

    void add_dependency(std::size_t from_prereq, std::size_t to_target) {
        adj_[from_prereq].push_back(to_target);
    }

    [[nodiscard]] std::optional<std::vector<std::size_t>> compute_toposort() const {
        std::vector<NodeColor> colors(adj_.size(), NodeColor::White);
        std::vector<std::size_t> post_order;
        post_order.reserve(adj_.size());

        for (std::size_t i = 0; i < adj_.size(); ++i) {
            if (colors[i] == NodeColor::White) {
                if (!visit_node(i, colors, post_order)) {
                    return std::nullopt; // Знайдено цикл
                }
            }
        }

        return post_order;
    }

private:
    bool visit_node(std::size_t u, std::vector<NodeColor>& colors,
                    std::vector<std::size_t>& post_order) const {
        colors[u] = NodeColor::Gray;

        for (std::size_t v : adj_[u]) {
            if (colors[v] == NodeColor::Gray) {
                return false; // Ребро веде на предка в стеку — цикл
            }
            if (colors[v] == NodeColor::White) {
                if (!visit_node(v, colors, post_order)) {
                    return false;
                }
            }
        }

        colors[u] = NodeColor::Black;
        post_order.push_back(u);
        return true;
    }

    std::vector<std::vector<std::size_t>> adj_;
};
