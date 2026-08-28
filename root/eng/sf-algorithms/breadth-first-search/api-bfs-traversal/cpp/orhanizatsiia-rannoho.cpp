#include <stdexcept>
#include <iostream>
#include <vector>

struct EarlyExitException : public std::exception {};

class TargetSearchVisitor : public default_bfs_visitor {
private:
    int target_;
    int target_distance_ = -1;
    std::vector<int> dist_;

public:
    explicit TargetSearchVisitor(int target, std::size_t num_vertices)
        : target_(target), dist_(num_vertices, -1) {}

    void start_vertex(int u) {
        dist_[u] = 0;
    }

    void tree_edge(int u, int v) {
        dist_[v] = dist_[u] + 1;
        if (v == target_) {
            target_distance_ = dist_[v];
            throw EarlyExitException(); // Дострокове переривання обходу!
        }
    }

    int get_target_distance() const { return target_distance_; }
};

void run_example_cpp(const std::vector<std::vector<int>>& graph, int start, int target) {
    TargetSearchVisitor visitor(target, graph.size());
    try {
        breadth_first_search_generic(graph, start, visitor);
        std::cout << "Вершина недосяжна\n";
    } catch (const EarlyExitException&) {
        std::cout << "Знайдено найкоротшу відстань: " << visitor.get_target_distance() << "\n";
    }
}
