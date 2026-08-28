#include <iostream>
#include <memory>
#include <random>
#include <utility>

template <typename KeyType>
class ExplicitTreap {
private:
    struct Node {
        KeyType key;
        uint32_t priority;
        std::unique_ptr<Node> left;
        std::unique_ptr<Node> right;

        Node(KeyType k, uint32_t p)
            : key(std::move(k)), priority(p), left(nullptr), right(nullptr) {}
    };

    using NodePtr = std::unique_ptr<Node>;
    NodePtr root_{nullptr};
    std::mt19937 rng_{std::random_device{}()};

    void split(NodePtr t, const KeyType& k, NodePtr& l, NodePtr& r) {
        if (!t) {
            l = nullptr;
            r = nullptr;
            return;
        }
        if (t->key <= k) {
            split(std::move(t->right), k, t->right, r);
            l = std::move(t);
        } else {
            split(std::move(t->left), k, l, t->left);
            r = std::move(t);
        }
    }

    NodePtr merge(NodePtr l, NodePtr r) {
        if (!l) return r;
        if (!r) return l;
        if (l->priority > r->priority) {
            l->right = merge(std::move(l->right), std::move(r));
            return l;
        } else {
            r->left = merge(std::move(l), std::move(r->left));
            return r;
        }
    }

public:
    ExplicitTreap() = default;

    void insert(KeyType key) {
        NodePtr l, r;
        split(std::move(root_), key, l, r);
        auto m = std::make_unique<Node>(std::move(key), static_cast<uint32_t>(rng_()));
        root_ = merge(merge(std::move(l), std::move(m)), std::move(r));
    }

    void erase(const KeyType& key) {
        NodePtr l, m, r;
        split(std::move(root_), key - 1, l, r);
        split(std::move(r), key, m, r);
        root_ = merge(std::move(l), std::move(r));
    }

    [[nodiscard]] bool contains(const KeyType& key) const noexcept {
        const Node* curr = root_.get();
        while (curr) {
            if (curr->key == key) return true;
            curr = (key < curr->key) ? curr->left.get() : curr->right.get();
        }
        return false;
    }
};
