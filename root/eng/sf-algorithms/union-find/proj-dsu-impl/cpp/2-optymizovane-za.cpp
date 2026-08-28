#include <vector>
#include <cstddef>
#include <cmath>

class CompactDSU {
public:
    explicit CompactDSU(std::size_t n)
        : parent_or_size_(n, -1), num_sets_(n) {}

    // Ітеративне уполовинення шляху (Path Halving)
    [[nodiscard]] int find(int x) noexcept {
        while (parent_or_size_[x] >= 0) {
            if (parent_or_size_[parent_or_size_[x]] >= 0) {
                parent_or_size_[x] = parent_or_size_[parent_or_size_[x]];
            }
            x = parent_or_size_[x];
        }
        return x;
    }

    bool unite(int x, int y) noexcept {
        int root_x = find(x);
        int root_y = find(y);

        if (root_x == root_y) {
            return false;
        }

        // parent_or_size_ зберігає -size, тому менше значення означає більший розмір
        if (parent_or_size_[root_x] < parent_or_size_[root_y]) {
            parent_or_size_[root_x] += parent_or_size_[root_y];
            parent_or_size_[root_y] = root_x;
        } else {
            parent_or_size_[root_y] += parent_or_size_[root_x];
            parent_or_size_[root_x] = root_y;
        }

        num_sets_--;
        return true;
    }

    [[nodiscard]] int set_size(int x) noexcept {
        return -parent_or_size_[find(x)];
    }

    [[nodiscard]] std::size_t num_sets() const noexcept {
        return num_sets_;
    }

private:
    std::vector<int> parent_or_size_;
    std::size_t num_sets_;
};
