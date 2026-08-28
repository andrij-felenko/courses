#include <iostream>
#include <vector>
#include <cstdint>
#include <algorithm>
#include <bitset>
#include <numeric>
#include <stdexcept>

constexpr size_t MAX_VERTICES = 64;

class Graph {
public:
    explicit Graph(size_t num_vertices) 
        : num_vertices_(std::min(num_vertices, MAX_VERTICES)), 
          adj_(num_vertices_, 0ULL) {}

    void add_edge(size_t u, size_t v) {
        if (u >= num_vertices_ || v >= num_vertices_) {
            throw std::out_of_range("Індекс вершини виходить за межі графа");
        }
        if (u != v) {
            adj_[u] |= (1ULL << v);
            adj_[v] |= (1ULL << u);
        }
    }

    [[nodiscard]] size_t size() const noexcept { return num_vertices_; }
    [[nodiscard]] uint64_t neighbors(size_t v) const noexcept { return adj_[v]; }
    [[nodiscard]] size_t degree(size_t v) const noexcept {
        return static_cast<size_t>(__builtin_popcountll(adj_[v]));
    }

private:
    size_t num_vertices_;
    std::vector<uint64_t> adj_;
};

struct ColoringResult {
    std::vector<int> colors;
    int chromatic_number{0};
    bool is_valid{false};
    uint64_t iterations{0};
};
