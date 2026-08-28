#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <unordered_map>
#include <expected>
#include <cstdint>

enum class DeBruijnError {
    InvalidParameters,
    MemoryAllocationFailed,
    GraphNotEulerian
};

class DeBruijnSequenceGenerator {
public:
    explicit DeBruijnSequenceGenerator(std::size_t k, std::size_t n)
        : k_(k), n_(n) {
        num_nodes_ = 1;
        for (std::size_t i = 0; i < n - 1; ++i) {
            num_nodes_ *= k;
        }
        num_edges_ = num_nodes_ * k;
    }

    [[nodiscard]] std::expected<std::string, DeBruijnError> generate() const {
        if (k_ < 2 || n_ < 1 || n_ > 20) {
            return std::unexpected(DeBruijnError::InvalidParameters);
        }

        std::vector<std::size_t> adj_count(num_nodes_, k_);
        std::vector<std::size_t> node_stack;
        std::vector<std::size_t> edge_stack;
        node_stack.reserve(num_edges_ + 1);
        edge_stack.reserve(num_edges_ + 1);

        std::string result;
        result.reserve(num_edges_);

        std::size_t curr_node = 0;
        const std::size_t mask = num_nodes_ - 1;

        node_stack.push_back(curr_node);
        edge_stack.push_back(0);

        while (!node_stack.empty()) {
            curr_node = node_stack.back();
            if (adj_count[curr_node] == 0) {
                if (node_stack.size() > 1) {
                    result.push_back(static_cast<char>('0' + edge_stack.back()));
                }
                node_stack.pop_back();
                edge_stack.pop_back();
            } else {
                --adj_count[curr_node];
                const std::size_t symbol = adj_count[curr_node];
                
                std::size_t next_node = 0;
                if (k_ == 2) {
                    next_node = ((curr_node << 1) | symbol) & mask;
                } else {
                    next_node = (curr_node * k_ + symbol) % num_nodes_;
                }

                node_stack.push_back(next_node);
                edge_stack.push_back(symbol);
            }
        }

        return result;
    }

private:
    std::size_t k_;
    std::size_t n_;
    std::size_t num_nodes_;
    std::size_t num_edges_;
};

int main() {
    DeBruijnSequenceGenerator generator(2, 3);
    auto result = generator.generate();

    if (result) {
        std::cout << "Генерована послідовність B(2, 3): " << *result << "\n";
    } else {
        std::cerr << "Помилка генерації послідовності!\n";
    }

    return 0;
}
