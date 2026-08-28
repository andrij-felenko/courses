#include <vector>
#include <algorithm>
#include <cstddef>
#include <span>

struct SegmentNode {
    long long total_sum{0};
    long long max_prefix{0};
    long long max_suffix{0};
    long long max_subarray{0};

    static SegmentNode make_leaf(long long val) noexcept {
        return SegmentNode{val, val, val, val};
    }

    static SegmentNode merge(const SegmentNode& L, const SegmentNode& R) noexcept {
        return SegmentNode{
            .total_sum = L.total_sum + R.total_sum,
            .max_prefix = std::max(L.max_prefix, L.total_sum + R.max_prefix),
            .max_suffix = std::max(R.max_suffix, R.total_sum + L.max_suffix),
            .max_subarray = std::max({L.max_subarray, R.max_subarray, L.max_suffix + R.max_prefix})
        };
    }
};

class KadaneSegmentTree {
public:
    explicit KadaneSegmentTree(std::span<const int> arr) : n_(arr.size()), tree_(4 * arr.size()) {
        if (!arr.empty()) {
            build(arr, 1, 0, n_ - 1);
        }
    }

    void update(std::size_t pos, long long new_val) noexcept {
        update_impl(1, 0, n_ - 1, pos, new_val);
    }

    [[nodiscard]] long long query_max_subarray(std::size_t l, std::size_t r) const noexcept {
        return query_impl(1, 0, n_ - 1, l, r).max_subarray;
    }

private:
    std::size_t n_{0};
    std::vector<SegmentNode> tree_;

    void build(std::span<const int> arr, std::size_t v, std::size_t tl, std::size_t tr) noexcept {
        if (tl == tr) {
            tree_[v] = SegmentNode::make_leaf(arr[tl]);
            return;
        }
        std::size_t tm = (tl + tr) / 2;
        build(arr, 2 * v, tl, tm);
        build(arr, 2 * v + 1, tm + 1, tr);
        tree_[v] = SegmentNode::merge(tree_[2 * v], tree_[2 * v + 1]);
    }

    void update_impl(std::size_t v, std::size_t tl, std::size_t tr, std::size_t pos, long long val) noexcept {
        if (tl == tr) {
            tree_[v] = SegmentNode::make_leaf(val);
            return;
        }
        std::size_t tm = (tl + tr) / 2;
        if (pos <= tm) {
            update_impl(2 * v, tl, tm, pos, val);
        } else {
            update_impl(2 * v + 1, tm + 1, tr, pos, val);
        }
        tree_[v] = SegmentNode::merge(tree_[2 * v], tree_[2 * v + 1]);
    }

    SegmentNode query_impl(std::size_t v, std::size_t tl, std::size_t tr, std::size_t l, std::size_t r) const noexcept {
        if (l <= tl && tr <= r) {
            return tree_[v];
        }
        std::size_t tm = (tl + tr) / 2;
        if (r <= tm) {
            return query_impl(2 * v, tl, tm, l, r);
        }
        if (l > tm) {
            return query_impl(2 * v + 1, tm + 1, tr, l, r);
        }
        return SegmentNode::merge(
            query_impl(2 * v, tl, tm, l, r),
            query_impl(2 * v + 1, tm + 1, tr, l, r)
        );
    }
};
