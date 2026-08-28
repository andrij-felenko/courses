// C++20 implementation: Idiomatic zero-allocation Savitch reachability solver
#include <iostream>
#include <vector>
#include <span>
#include <cstdint>
#include <expected>
#include <system_error>

namespace space_complexity {

class GraphView {
public:
    explicit GraphView(uint32_t vertices, std::span<const uint8_t> matrix_data)
        : num_vertices_(vertices), matrix_(matrix_data) {}

    [[nodiscard]] bool has_edge(uint32_t u, uint32_t v) const noexcept {
        if (u >= num_vertices_ || v >= num_vertices_) {
            return false;
        }
        return matrix_[u * num_vertices_ + v] != 0;
    }

    [[nodiscard]] uint32_t size() const noexcept {
        return num_vertices_;
    }

private:
    uint32_t num_vertices_;
    std::span<const uint8_t> matrix_;
};

enum class ReachabilityError {
    InvalidVertexIndex,
    MaxDepthExceeded
};

class SavitchSolver {
public:
    // Evaluates if target is reachable from source within given steps
    [[nodiscard]] static std::expected<bool, ReachabilityError> is_reachable(
        const GraphView& graph, uint32_t source, uint32_t target) noexcept 
    {
        if (source >= graph.size() || target >= graph.size()) {
            return std::unexpected(ReachabilityError::InvalidVertexIndex);
        }
        return can_reach_recursive(graph, source, target, graph.size());
    }

private:
    static bool can_reach_recursive(
        const GraphView& graph, uint32_t u, uint32_t v, uint32_t steps) noexcept 
    {
        if (u == v) {
            return true;
        }
        if (steps == 1) {
            return graph.has_edge(u, v);
        }

        const uint32_t half_steps = (steps + 1) / 2;

        for (uint32_t w = 0; w < graph.size(); ++w) {
            if (can_reach_recursive(graph, u, w, half_steps) &&
                can_reach_recursive(graph, w, v, steps - half_steps)) {
                return true;
            }
        }

        return false;
    }
};

} // namespace space_complexity

int main() {
    constexpr uint32_t N = 5;
    const std::vector<uint8_t> adj_matrix = {
        0, 1, 0, 0, 0,
        0, 0, 1, 0, 0,
        0, 0, 0, 1, 0,
        0, 0, 0, 0, 1,
        0, 0, 0, 0, 0
    };

    space_complexity::GraphView graph(N, adj_matrix);
    
    auto result = space_complexity::SavitchSolver::is_reachable(graph, 0, 4);

    if (result.has_value()) {
        std::cout << "Reachable: " << std::boolalpha << result.value() << "\n";
    } else {
        std::cerr << "Reachability evaluation error occurred.\n";
    }

    return 0;
}
