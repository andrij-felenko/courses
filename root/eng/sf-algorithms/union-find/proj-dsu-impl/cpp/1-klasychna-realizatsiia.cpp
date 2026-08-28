#include <vector>
#include <cstddef>
#include <numeric>
#include <stdexcept>

class DisjointSetUnion {
public:
    explicit DisjointSetUnion(std::size_t n)
        : parent_(n), rank_(n, 0), num_sets_(n) {
        std::iota(parent_.begin(), parent_.end(), 0);
    }

    [[nodiscard]] std::size_t find(std::size_t x) {
        if (x >= parent_.size()) {
            throw std::out_of_range("Індекс вузла виходить за межі DSU");
        }
        // Рекурсивне стиснення шляху
        if (parent_[x] != x) {
            parent_[x] = find(parent_[x]);
        }
        return parent_[x];
    }

    bool unite(std::size_t x, std::size_t y) {
        const std::size_t root_x = find(x);
        const std::size_t root_y = find(y);

        if (root_x == root_y) {
            return false;
        }

        // Об'єднання за рангом
        if (rank_[root_x] < rank_[root_y]) {
            parent_[root_x] = root_y;
        } else if (rank_[root_x] > rank_[root_y]) {
            parent_[root_y] = root_x;
        } else {
            parent_[root_y] = root_x;
            rank_[root_x]++;
        }

        num_sets_--;
        return true;
    }

    [[nodiscard]] bool connected(std::size_t x, std::size_t y) {
        return find(x) == find(y);
    }

    [[nodiscard]] std::size_t num_sets() const noexcept {
        return num_sets_;
    }

private:
    std::vector<std::size_t> parent_;
    std::vector<std::size_t> rank_;
    std::size_t num_sets_;
};
