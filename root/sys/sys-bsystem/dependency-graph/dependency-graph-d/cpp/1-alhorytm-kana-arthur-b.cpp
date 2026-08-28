#include <vector>
#include <queue>
#include <optional>
#include <cstddef>

class BuildGraph {
public:
    explicit BuildGraph(std::size_t node_count)
        : adj_(node_count), in_degree_(node_count, 0) {}

    void add_dependency(std::size_t from_prereq, std::size_t to_target) {
        adj_[from_prereq].push_back(to_target);
        ++in_degree_[to_target];
    }

    [[nodiscard]] std::optional<std::vector<std::size_t>> compute_schedule() const {
        std::vector<std::size_t> degrees = in_degree_;
        std::queue<std::size_t> ready_queue;
        std::vector<std::size_t> linear_order;
        linear_order.reserve(adj_.size());

        for (std::size_t i = 0; i < degrees.size(); ++i) {
            if (degrees[i] == 0) {
                ready_queue.push(i);
            }
        }

        while (!ready_queue.empty()) {
            std::size_t current = ready_queue.front();
            ready_queue.pop();
            linear_order.push_back(current);

            for (std::size_t dependent : adj_[current]) {
                if (--degrees[dependent] == 0) {
                    ready_queue.push(dependent);
                }
            }
        }

        if (linear_order.size() != adj_.size()) {
            return std::nullopt; // Виявлено цикл
        }

        return linear_order;
    }

private:
    std::vector<std::vector<std::size_t>> adj_;
    std::vector<std::size_t> in_degree_;
};
