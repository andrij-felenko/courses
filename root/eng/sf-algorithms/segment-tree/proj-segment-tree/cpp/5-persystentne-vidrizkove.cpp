#include <memory>
#include <vector>
#include <span>
#include <cstddef>
#include <algorithm>

class PersistentSegmentTree {
    struct Node {
        long long val{0};
        std::shared_ptr<Node> left{nullptr};
        std::shared_ptr<Node> right{nullptr};
    };

public:
    explicit PersistentSegmentTree(std::span<const long long> data)
        : n_(data.size()) {
        if (!data.empty()) {
            roots_.push_back(build(0, n_ - 1, data));
        }
    }

    std::size_t update_point(std::size_t version, std::size_t index, long long new_val) {
        auto new_root = update_impl(roots_[version], 0, n_ - 1, index, new_val);
        roots_.push_back(new_root);
        return roots_.size() - 1;
    }

    [[nodiscard]] long long query_range(std::size_t version, std::size_t left, std::size_t right) const {
        return query_impl(roots_[version], 0, n_ - 1, left, right);
    }

private:
    std::size_t n_;
    std::vector<std::shared_ptr<Node>> roots_;

    std::shared_ptr<Node> build(std::size_t tl, std::size_t tr, std::span<const long long> data) {
        auto node = std::make_shared<Node>();
        if (tl == tr) {
            node->val = data[tl];
            return node;
        }
        std::size_t tm = tl + (tr - tl) / 2;
        node->left = build(tl, tm, data);
        node->right = build(tm + 1, tr, data);
        node->val = node->left->val + node->right->val;
        return node;
    }

    std::shared_ptr<Node> update_impl(const std::shared_ptr<Node>& prev, std::size_t tl, std::size_t tr, std::size_t pos, long long new_val) {
        auto node = std::make_shared<Node>();
        if (tl == tr) {
            node->val = new_val;
            return node;
        }
        std::size_t tm = tl + (tr - tl) / 2;
        if (pos <= tm) {
            node->left = update_impl(prev->left, tl, tm, pos, new_val);
            node->right = prev->right;
        } else {
            node->left = prev->left;
            node->right = update_impl(prev->right, tm + 1, tr, pos, new_val);
        }
        node->val = node->left->val + node->right->val;
        return node;
    }

    long long query_impl(const std::shared_ptr<Node>& node, std::size_t tl, std::size_t tr, std::size_t l, std::size_t r) const {
        if (!node || l > r) return 0;
        if (l == tl && r == tr) return node->val;
        std::size_t tm = tl + (tr - tl) / 2;
        std::size_t left_r = std::min(r, tm);
        std::size_t right_l = std::max(l, tm + 1);
        long long res_l = (l <= tm) ? query_impl(node->left, tl, tm, l, left_r) : 0;
        long long res_r = (r > tm) ? query_impl(node->right, tm + 1, tr, right_l, r) : 0;
        return res_l + res_r;
    }
};
