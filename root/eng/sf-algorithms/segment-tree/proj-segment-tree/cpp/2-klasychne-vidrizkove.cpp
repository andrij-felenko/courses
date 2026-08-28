#include <vector>
#include <span>
#include <functional>
#include <stdexcept>
#include <cstddef>
#include <algorithm>

template <typename T, typename CombineOp = std::plus<T>>
class SegmentTree {
public:
    explicit SegmentTree(std::span<const T> data, T identity = T{}, CombineOp op = CombineOp{})
        : n_(data.size()), identity_(identity), op_(op), tree_(4 * data.size(), identity) {
        if (!data.empty()) {
            build(0, 0, n_ - 1, data);
        }
    }

    void update_point(std::size_t index, const T& value) {
        if (index >= n_) {
            throw std::out_of_range("SegmentTree::update_point index out of bounds");
        }
        update_point_impl(0, 0, n_ - 1, index, value);
    }

    [[nodiscard]] T query_range(std::size_t left, std::size_t right) const {
        if (left > right || right >= n_) {
            return identity_;
        }
        return query_range_impl(0, 0, n_ - 1, left, right);
    }

    [[nodiscard]] std::size_t size() const noexcept { return n_; }

private:
    std::size_t n_;
    T identity_;
    CombineOp op_;
    std::vector<T> tree_;

    static constexpr std::size_t left_child(std::size_t v) noexcept { return 2 * v + 1; }
    static constexpr std::size_t right_child(std::size_t v) noexcept { return 2 * v + 2; }

    void build(std::size_t v, std::size_t tl, std::size_t tr, std::span<const T> data) {
        if (tl == tr) {
            tree_[v] = data[tl];
            return;
        }
        std::size_t tm = tl + (tr - tl) / 2;
        build(left_child(v), tl, tm, data);
        build(right_child(v), tm + 1, tr, data);
        tree_[v] = op_(tree_[left_child(v)], tree_[right_child(v)]);
    }

    void update_point_impl(std::size_t v, std::size_t tl, std::size_t tr, std::size_t pos, const T& value) {
        if (tl == tr) {
            tree_[v] = value;
            return;
        }
        std::size_t tm = tl + (tr - tl) / 2;
        if (pos <= tm) {
            update_point_impl(left_child(v), tl, tm, pos, value);
        } else {
            update_point_impl(right_child(v), tl, tm + 1, tr, pos, value);
        }
        tree_[v] = op_(tree_[left_child(v)], tree_[right_child(v)]);
    }

    T query_range_impl(std::size_t v, std::size_t tl, std::size_t tr, std::size_t l, std::size_t r) const {
        if (l > r) return identity_;
        if (l == tl && r == tr) {
            return tree_[v];
        }
        std::size_t tm = tl + (tr - tl) / 2;
        std::size_t left_r = std::min(r, tm);
        std::size_t right_l = std::max(l, tm + 1);

        T res_left = (l <= tm) ? query_range_impl(left_child(v), tl, tm, l, left_r) : identity_;
        T res_right = (r > tm) ? query_range_impl(right_child(v), tm + 1, tr, right_l, r) : identity_;

        return op_(res_left, res_right);
    }
};
