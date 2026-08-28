#include <iostream>
#include <memory>
#include <random>
#include <utility>

class ImplicitTreap {
private:
    struct Node {
        long long val;
        long long sum;
        int sz{1};
        bool rev{false};
        uint32_t priority;
        std::unique_ptr<Node> left{nullptr};
        std::unique_ptr<Node> right{nullptr};

        Node(long long v, uint32_t p)
            : val(v), sum(v), priority(p) {}
    };

    using NodePtr = std::unique_ptr<Node>;
    NodePtr root_{nullptr};
    std::mt19937 rng_{std::random_device{}()};

    static int getSize(const Node* n) noexcept {
        return n ? n->sz : 0;
    }

    static long long getSum(const Node* n) noexcept {
        return n ? n->sum : 0LL;
    }

    static void pushUp(Node* n) noexcept {
        if (!n) return;
        n->sz = 1 + getSize(n->left.get()) + getSize(n->right.get());
        n->sum = n->val + getSum(n->left.get()) + getSum(n->right.get());
    }

    static void pushDown(Node* n) noexcept {
        if (!n || !n->rev) return;
        std::swap(n->left, n->right);
        if (n->left) n->left->rev ^= true;
        if (n->right) n->right->rev ^= true;
        n->rev = false;
    }

    void split(NodePtr t, int k, NodePtr& l, NodePtr& r) {
        if (!t) {
            l = nullptr;
            r = nullptr;
            return;
        }
        pushDown(t.get());
        int leftSize = getSize(t->left.get());
        if (leftSize + 1 <= k) {
            split(std::move(t->right), k - leftSize - 1, t->right, r);
            l = std::move(t);
        } else {
            split(std::move(t->left), k, l, t->left);
            r = std::move(t);
        }
        pushUp(l.get());
        pushUp(r.get());
    }

    NodePtr merge(NodePtr l, NodePtr r) {
        pushDown(l.get());
        pushDown(r.get());
        if (!l) return r;
        if (!r) return l;
        if (l->priority > r->priority) {
            l->right = merge(std::move(l->right), std::move(r));
            pushUp(l.get());
            return l;
        } else {
            r->left = merge(std::move(l), std::move(r->left));
            pushUp(r.get());
            return r;
        }
    }

public:
    ImplicitTreap() = default;

    [[nodiscard]] int size() const noexcept {
        return getSize(root_.get());
    }

    void insertAt(int pos, long long val) {
        NodePtr l, r;
        split(std::move(root_), pos - 1, l, r);
        auto m = std::make_unique<Node>(val, static_cast<uint32_t>(rng_()));
        root_ = merge(merge(std::move(l), std::move(m)), std::move(r));
    }

    void eraseAt(int pos) {
        NodePtr l, m, r;
        split(std::move(root_), pos - 1, l, r);
        split(std::move(r), 1, m, r);
        root_ = merge(std::move(l), std::move(r));
    }

    void reverseRange(int lIdx, int rIdx) {
        NodePtr l, m, r;
        split(std::move(root_), lIdx - 1, l, r);
        split(std::move(r), rIdx - lIdx + 1, m, r);
        if (m) m->rev ^= true;
        root_ = merge(merge(std::move(l), std::move(m)), std::move(r));
    }

    [[nodiscard]] long long querySum(int lIdx, int rIdx) {
        NodePtr l, m, r;
        split(std::move(root_), lIdx - 1, l, r);
        split(std::move(r), rIdx - lIdx + 1, m, r);
        long long result = getSum(m.get());
        root_ = merge(merge(std::move(l), std::move(m)), std::move(r));
        return result;
    }
};
