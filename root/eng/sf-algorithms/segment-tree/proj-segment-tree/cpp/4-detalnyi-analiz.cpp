#include <vector>
#include <span>
#include <cstddef>
#include <algorithm>

class LazySegmentTree {
public:
    explicit LazySegmentTree(std::size_t n)
        : n_(n), tree_(4 * n, 0), lazy_(4 * n, 0) {}

    explicit LazySegmentTree(std::span<const long long> data)
        : n_(data.size()), tree_(4 * data.size(), 0), lazy_(4 * data.size(), 0) {
        if (!data.empty()) {
            build(0, 0, n_ - 1, data);
        }
    }

    void update_range(std::size_t left, std::size_t right, long long add_value) {
        if (left > right || right >= n_) return;
        update_range_impl(0, 0, n_ - 1, left, right, add_value);
    }

    [[nodiscard]] long long query_range(std::size_t left, std::size_t right) {
        if (left > right || right >= n_) return 0;
        return query_range_impl(0, 0, n_ - 1, left, right);
    }

private:
    std::size_t n_;
    std::vector<long long> tree_;
    std::vector<long long> lazy_;

    static constexpr std::size_t left_child(std::size_t v) noexcept { return 2 * v + 1; }
    static constexpr std::size_t right_child(std::size_t v) noexcept { return 2 * v + 2; }

    void build(std::size_t v, std::size_t tl, std::size_t tr, std::span<const long long> data) {
        if (tl == tr) {
            tree_[v] = data[tl];
            return;
        }
        std::size_t tm = tl + (tr - tl) / 2;
        build(left_child(v), tl, tm, data);
        build(right_child(v), tm + 1, tr, data);
        tree_[v] = tree_[left_child(v)] + tree_[right_child(v)];
    }

    void push_down(std::size_t v, std::size_t tl, std::size_t tr) {
        if (lazy_[v] != 0 && tl != tr) {
            std::size_t tm = tl + (tr - tl) / 2;
            std::size_t lc = left_child(v);
            std::size_t rc = right_child(v);

            lazy_[lc] += lazy_[v];
            tree_[lc] += lazy_[v] * static_cast<long long>(tm - tl + 1);

            lazy_[rc] += lazy_[v];
            tree_[rc] += lazy_[v] * static_cast<long long>(tr - tm);

            lazy_[v] = 0;
        }
    }

    void update_range_impl(std::size_t v, std::size_t tl, std::size_t tr, std::size_t l, std::size_t r, long long val) {
        if (l > r) return;
        if (l == tl && r == tr) {
            tree_[v] += val * static_cast<long long>(tr - tl + 1);
            lazy_[v] += val;
            return;
        }
        push_down(v, tl, tr);
        std::size_t tm = tl + (tr - tl) / 2;
        std::size_t left_r = std::min(r, tm);
        std::size_t right_l = std::max(l, tm + 1);

        if (l <= tm) update_range_impl(left_child(v), tl, tm, l, left_r, val);
        if (r > tm) update_range_impl(right_child(v), tm + 1, tr, right_l, r, val);

        tree_[v] = tree_[left_child(v)] + tree_[right_child(v)];
    }

    long long query_range_impl(std::size_t v, std::size_t tl, std::size_t tr, std::size_t l, std::size_t r) {
        if (l > r) return 0;
        if (l == tl && r == tr) {
            return tree_[v];
        }
        push_down(v, tl, tr);
        std::size_t tm = tl + (tr - tl) / 2;
        std::size_t left_r = std::min(r, tm);
        std::size_t right_l = std::max(l, tm + 1);

        long long res_left = (l <= tm) ? query_range_impl(left_child(v), tl, tm, l, left_r) : 0;
        long long res_right = (r > tm) ? query_range_impl(right_child(v), tm + 1, tr, right_l, r) : 0;

        return res_left + res_right;
    }
};
