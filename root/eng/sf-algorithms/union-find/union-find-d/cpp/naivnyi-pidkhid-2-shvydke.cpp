#include <vector>
#include <cstddef>
#include <numeric>

// Реалізація Quick-Union мовою C++
class QuickUnionDSU {
public:
    explicit QuickUnionDSU(std::size_t n) : parent_(n) {
        std::iota(parent_.begin(), parent_.end(), 0);
    }

    [[nodiscard]] std::size_t find(std::size_t x) const noexcept {
        while (x != parent_[x]) {
            x = parent_[x];
        }
        return x;
    }

    void unite(std::size_t x, std::size_t y) noexcept {
        std::size_t root_x = find(x);
        std::size_t root_y = find(y);
        if (root_x != root_y) {
            parent_[root_x] = root_y;
        }
    }

private:
    std::vector<std::size_t> parent_;
};
