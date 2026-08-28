#include <iostream>
#include <vector>
#include <algorithm>

class DegreeStatsVisitor : public default_bfs_visitor {
private:
    int max_degree_ = 0;
    std::size_t visited_count_ = 0;

public:
    void examine_vertex(int /*u*/) {
        visited_count_++;
    }

    std::size_t get_visited_count() const { return visited_count_; }
};

void analyze_degrees_cpp(const std::vector<std::vector<int>>& graph, int start) {
    DegreeStatsVisitor visitor;
    breadth_first_search_generic(graph, start, visitor);
    std::cout << "Оброблено вершин: " << visitor.get_visited_count() << "\n";
}
