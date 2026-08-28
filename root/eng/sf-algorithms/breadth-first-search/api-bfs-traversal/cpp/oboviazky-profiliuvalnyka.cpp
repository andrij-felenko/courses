#include <vector>
#include <cstddef>

class MemoryProfilerVisitor : public default_bfs_visitor {
private:
    std::size_t current_queue_size_ = 0;
    std::size_t peak_queue_size_ = 0;
    std::size_t total_edges_examined_ = 0;

public:
    void discover_vertex(int /*u*/) {
        current_queue_size_++;
        if (current_queue_size_ > peak_queue_size_) {
            peak_queue_size_ = current_queue_size_;
        }
    }

    void examine_vertex(int /*u*/) {
        if (current_queue_size_ > 0) {
            current_queue_size_--;
        }
    }

    void examine_edge(int /*u*/, int /*v*/) {
        total_edges_examined_++;
    }

    std::size_t get_peak_queue_size() const { return peak_queue_size_; }
    std::size_t get_total_edges_examined() const { return total_edges_examined_; }
};

void profile_bfs_cpp(const std::vector<std::vector<int>>& graph, int start) {
    MemoryProfilerVisitor visitor;
    breadth_first_search_generic(graph, start, visitor);
}
