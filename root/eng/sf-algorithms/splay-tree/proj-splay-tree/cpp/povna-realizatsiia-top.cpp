#include <iostream>
#include <memory>
#include <optional>
#include <utility>
#include <concepts>

template <typename Key, typename Value, typename Compare = std::less<Key>>
class SplayTree {
public:
    struct Node {
        Key key;
        Value value;
        std::unique_ptr<Node> left{nullptr};
        std::unique_ptr<Node> right{nullptr};

        Node(Key k, Value v) : key(std::move(k)), value(std::move(v)) {}
    };

private:
    std::unique_ptr<Node> root_{nullptr};
    std::size_t size_{0};
    [[no_unique_address]] Compare comp_{};

    // Оптимізована операція Top-Down Splay з безпечною передачею унікальних покажчиків
    std::unique_ptr<Node> splay(std::unique_ptr<Node> t, const Key& key) {
        if (!t) return nullptr;

        Node dummy{Key{}, Value{}};
        Node* l = &dummy;
        Node* r = &dummy;

        while (true) {
            if (comp_(key, t->key)) {
                if (!t->left) break;
                if (comp_(key, t->left->key)) {
                    // Zig-Zig праворуч
                    auto y = std::move(t->left);
                    t->left = std::move(y->right);
                    y->right = std::move(t);
                    t = std::move(y);
                    if (!t->left) break;
                }
                r->left = std::move(t);
                r = r->left.get();
                t = std::move(r->left);
            } else if (comp_(t->key, key)) {
                if (!t->right) break;
                if (comp_(t->right->key, key)) {
                    // Zig-Zig ліворуч
                    auto y = std::move(t->right);
                    t->right = std::move(y->left);
                    y->left = std::move(t);
                    t = std::move(y);
                    if (!t->right) break;
                }
                l->right = std::move(t);
                l = l->right.get();
                t = std::move(l->right);
            } else {
                break;
            }
        }

        l->right = std::move(t->left);
        r->left = std::move(t->right);
        t->left = std::move(dummy.right);
        t->right = std::move(dummy.left);

        return t;
    }

public:
    SplayTree() = default;
    ~SplayTree() = default;

    SplayTree(const SplayTree&) = delete;
    SplayTree& operator=(const SplayTree&) = delete;

    SplayTree(SplayTree&&) noexcept = default;
    SplayTree& operator=(SplayTree&&) noexcept = default;

    [[nodiscard]] std::size_t size() const noexcept { return size_; }
    [[nodiscard]] bool empty() const noexcept { return size_ == 0; }

    bool insert(Key key, Value value) {
        if (!root_) {
            root_ = std::make_unique<Node>(std::move(key), std::move(value));
            size_ = 1;
            return true;
        }

        root_ = splay(std::move(root_), key);

        if (!comp_(key, root_->key) && !comp_(root_->key, key)) {
            root_->value = std::move(value);
            return false;
        }

        auto new_node = std::make_unique<Node>(std::move(key), std::move(value));
        if (comp_(new_node->key, root_->key)) {
            new_node->left = std::move(root_->left);
            new_node->right = std::move(root_);
        } else {
            new_node->right = std::move(root_->right);
            new_node->left = std::move(root_);
        }

        root_ = std::move(new_node);
        ++size_;
        return true;
    }

    [[nodiscard]] std::optional<Value> find(const Key& key) {
        if (!root_) return std::nullopt;

        root_ = splay(std::move(root_), key);
        if (!comp_(key, root_->key) && !comp_(root_->key, key)) {
            return root_->value;
        }
        return std::nullopt;
    }

    [[nodiscard]] bool contains(const Key& key) {
        return find(key).has_value();
    }

    bool erase(const Key& key) {
        if (!root_) return false;

        root_ = splay(std::move(root_), key);
        if (comp_(key, root_->key) || comp_(root_->key, key)) {
            return false;
        }

        if (!root_->left) {
            root_ = std::move(root_->right);
        } else {
            auto right_subtree = std::move(root_->right);
            root_ = splay(std::move(root_->left), key);
            root_->right = std::move(right_subtree);
        }

        --size_;
        return true;
    }
};
