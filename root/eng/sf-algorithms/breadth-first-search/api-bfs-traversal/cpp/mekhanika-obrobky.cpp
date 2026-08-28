#include <iostream>
#include <vector>
#include <cstdint>

class NetworkTimeoutVisitor : public default_bfs_visitor {
private:
    std::uint32_t max_rtt_ms_;
    std::size_t failed_edges_count_ = 0;

public:
    explicit NetworkTimeoutVisitor(std::uint32_t max_rtt_ms)
        : max_rtt_ms_(max_rtt_ms) {}

    void examine_edge(int u, int v) {
        std::uint32_t simulated_rtt = static_cast<std::uint32_t>((u * 17 + v * 31) % 150);
        if (simulated_rtt > max_rtt_ms_) {
            failed_edges_count_++;
        }
    }

    std::size_t get_failed_edges_count() const { return failed_edges_count_; }
};

void run_network_bfs_cpp(const std::vector<std::vector<int>>& graph, int start, std::uint32_t max_rtt) {
    NetworkTimeoutVisitor visitor(max_rtt);
    breadth_first_search_generic(graph, start, visitor);
    std::cout << "Кількість ребер із тайм-аутом: " << visitor.get_failed_edges_count() << "\n";
}
