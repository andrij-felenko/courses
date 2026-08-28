#include <iostream>
#include <memory>
#include <utility>
#include <vector>

enum class Color { Red, Black };

template <typename T>
class RedBlackTree {
private:
    struct Node {
        T key;
        Color color;
        Node* left{nullptr};
        Node* right{nullptr};
        Node* parent{nullptr};

        explicit Node(T val, Color c = Color::Red) 
            : key(std::move(val)), color(c) {}
    };

    Node* root_{nullptr};
    Node* nil_{nullptr};

    void left_rotate(Node* x) {
        Node* y = x->right;
        x->right = y->left;

        if (y->left != nil_) {
            y->left->parent = x;
        }

        y->parent = x->parent;

        if (x->parent == nil_) {
            root_ = y;
        } else if (x == x->parent->left) {
            x->parent->left = y;
        } else {
            x->parent->right = y;
        }

        y->left = x;
        x->parent = y;
    }

    void right_rotate(Node* y) {
        Node* x = y->left;
        y->left = x->right;

        if (x->right != nil_) {
            x->right->parent = y;
        }

        x->parent = y->parent;

        if (y->parent == nil_) {
            root_ = x;
        } else if (y == y->parent->right) {
            y->parent->right = x;
        } else {
            y->parent->left = x;
        }

        x->right = y;
        y->parent = x;
    }

    void insert_fixup(Node* z) {
        while (z->parent->color == Color::Red) {
            if (z->parent == z->parent->parent->left) {
                Node* y = z->parent->parent->right; // Дядько
                if (y->color == Color::Red) {
                    z->parent->color = Color::Black;
                    y->color = Color::Black;
                    z->parent->parent->color = Color::Red;
                    z = z->parent->parent;
                } else {
                    if (z == z->parent->right) {
                        z = z->parent;
                        left_rotate(z);
                    }
                    z->parent->color = Color::Black;
                    z->parent->parent->color = Color::Red;
                    right_rotate(z->parent->parent);
                }
            } else {
                Node* y = z->parent->parent->left;
                if (y->color == Color::Red) {
                    z->parent->color = Color::Black;
                    y->color = Color::Black;
                    z->parent->parent->color = Color::Red;
                    z = z->parent->parent;
                } else {
                    if (z == z->parent->left) {
                        z = z->parent;
                        right_rotate(z);
                    }
                    z->parent->color = Color::Black;
                    z->parent->parent->color = Color::Red;
                    left_rotate(z->parent->parent);
                }
            }
        }
        root_->color = Color::Black;
    }

    void destroy_recursive(Node* node) {
        if (node != nil_) {
            destroy_recursive(node->left);
            destroy_recursive(node->right);
            delete node;
        }
    }

public:
    RedBlackTree() {
        nil_ = new Node(T{}, Color::Black);
        root_ = nil_;
    }

    ~RedBlackTree() {
        destroy_recursive(root_);
        delete nil_;
    }

    RedBlackTree(const RedBlackTree&) = delete;
    RedBlackTree& operator=(const RedBlackTree&) = delete;
    RedBlackTree(RedBlackTree&& o) noexcept 
        : root_(std::exchange(o.root_, nullptr)), nil_(std::exchange(o.nil_, nullptr)) {}

    RedBlackTree& operator=(RedBlackTree&& o) noexcept {
        if (this != &o) {
            if (root_) destroy_recursive(root_);
            delete nil_;
            root_ = std::exchange(o.root_, nullptr);
            nil_ = std::exchange(o.nil_, nullptr);
        }
        return *this;
    }

    void insert(T key) {
        Node* z = new Node(std::move(key), Color::Red);
        z->left = nil_;
        z->right = nil_;

        Node* y = nil_;
        Node* x = root_;

        while (x != nil_) {
            y = x;
            if (z->key < x->key) {
                x = x->left;
            } else {
                x = x->right;
            }
        }

        z->parent = y;
        if (y == nil_) {
            root_ = z;
        } else if (z->key < y->key) {
            y->left = z;
        } else {
            y->right = z;
        }

        insert_fixup(z);
    }

    [[nodiscard]] bool contains(const T& key) const {
        Node* curr = root_;
        while (curr != nil_) {
            if (key == curr->key) return true;
            if (key < curr->key) curr = curr->left;
            else curr = curr->right;
        }
        return false;
    }

    [[nodiscard]] const T& root_key() const {
        return root_->key;
    }
};

int main() {
    RedBlackTree<int> tree;
    for (int k : {10, 20, 30, 15, 25, 5}) {
        tree.insert(k);
    }
    std::cout << "Root key: " << tree.root_key() << "\n";
    std::cout << "Contains 15: " << std::boolalpha << tree.contains(15) << "\n";
    return 0;
}
