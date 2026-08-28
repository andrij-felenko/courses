#include <vector>
#include <cstddef>
#include <stdexcept>
#include <iostream>

class DenseTransitiveClosure {
private:
    size_t vertices_;
    std::vector<uint8_t> matrix_;

public:
    explicit DenseTransitiveClosure(size_t vertices)
        : vertices_(vertices), matrix_(vertices * vertices, 0) {
        if (vertices == 0) {
            throw std::invalid_argument("Graph must contain at least 1 vertex");
        }
    }

    void addEdge(size_t u, size_t v) {
        if (u >= vertices_ || v >= vertices_) {
            throw std::out_of_range("Vertex index out of graph bounds");
        }
        matrix_[u * vertices_ + v] = 1;
    }

    void computeWarshall() {
        const size_t v = vertices_;
        for (size_t k = 0; k < v; ++k) {
            for (size_t i = 0; i < v; ++i) {
                if (!matrix_[i * v + k]) continue;
                const size_t i_offset = i * v;
                const size_t k_offset = k * v;
                for (size_t j = 0; j < v; ++j) {
                    if (matrix_[k_offset + j]) {
                        matrix_[i_offset + j] = 1;
                    }
                }
            }
        }
    }

    [[nodiscard]] bool isReachable(size_t u, size_t v) const {
        if (u >= vertices_ || v >= vertices_) return false;
        return matrix_[u * vertices_ + v] != 0;
    }

    [[nodiscard]] size_t vertices() const noexcept { return vertices_; }
};
