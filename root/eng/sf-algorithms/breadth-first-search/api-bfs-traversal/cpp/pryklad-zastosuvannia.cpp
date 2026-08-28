#include <vector>
#include <algorithm>

class PathRecorderVisitor : public default_bfs_visitor {
private:
    std::vector<int>& parent_;

public:
    explicit PathRecorderVisitor(std::vector<int>& parent)
        : parent_(parent) {}

    void tree_edge(int u, int v) {
        parent_[v] = u;
    }
};

std::vector<int> reconstruct_path_cpp(int start, int target, const std::vector<int>& parent) {
    if (parent[target] == -1 && target != start) {
        return {}; // Ціль недосяжна
    }

    std::vector<int> path;
    for (int v = target; v != -1; v = parent[v]) {
        path.push_back(v);
    }
    std::reverse(path.begin(), path.end());
    return path;
}
