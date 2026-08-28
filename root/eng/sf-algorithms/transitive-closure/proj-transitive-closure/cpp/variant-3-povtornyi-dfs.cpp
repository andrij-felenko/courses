#include <vector>
#include <cstddef>
#include <stdexcept>

class SparseDFSTransitiveClosure {
private:
    size_t vertices_;
    std::vector<std::vector<size_t>> adj_;
    std::vector<uint8_t> matrix_;

    void dfs(size_t source, size_t curr) {
        for (size_t next_v : adj_[curr]) {
            if (!matrix_[source * vertices_ + next_v]) {
                matrix_[source * vertices_ + next_v] = 1;
                dfs(source, next_v);
            }
        }
    }

public:
    explicit SparseDFSTransitiveClosure(size_t vertices)
        : vertices_(vertices), adj_(vertices), matrix_(vertices * vertices, 0) {}

    void addEdge(size_t u, size_t v) {
        if (u >= vertices_ || v >= vertices_) return;
        adj_[u].push_back(v);
    }

    void compute() {
        for (size_t i = 0; i < vertices_; ++i) {
            dfs(i, i);
        }
    }

    [[nodiscard]] bool isReachable(size_t u, size_t v) const {
        if (u >= vertices_ || v >= vertices_) return false;
        return matrix_[u * vertices_ + v] != 0;
    }
};
