#include <vector>
#include <span>
#include <cstddef>

template <typename T>
class IterativeSegmentTree {
public:
    explicit IterativeSegmentTree(std::span<const T> data)
        : n_(data.size()), tree_(2 * data.size(), T{}) {
        for (std::size_t i = 0; i < n_; ++i) {
            tree_[n_ + i] = data[i];
        }
        for (std::size_t i = n_ - 1; i > 0; --i) {
            tree_[i] = tree_[i << 1] + tree_[(i << 1) | 1];
        }
    }

    void update(std::size_t pos, T val) {
        for (tree_[pos += n_] = val; pos > 1; pos >>= 1) {
            tree_[pos >> 1] = tree_[pos] + tree_[pos ^ 1];
        }
    }

    [[nodiscard]] T query(std::size_t left, std::size_t right) const {
        T res{};
        for (left += n_, right += n_; left < right; left >>= 1, right >>= 1) {
            if (left & 1) res = res + tree_[left++];
            if (right & 1) res = res + tree_[--right];
        }
        return res;
    }

private:
    std::size_t n_;
    std::vector<T> tree_;
};
