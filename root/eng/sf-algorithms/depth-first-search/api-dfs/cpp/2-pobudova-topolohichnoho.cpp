// C++20 реалізація топологічного сортування
#include <vector>
#include <algorithm>

class TopologicalSortVisitor : public algo::default_dfs_visitor {
private:
    std::vector<int> post_order_;

public:
    void finish_vertex(int u, int /*f_time*/) {
        post_order_.push_back(u);
    }

    [[nodiscard]] std::vector<int> get_topological_order() const {
        std::vector<int> result = post_order_;
        std::reverse(result.begin(), result.end());
        return result;
    }
};
