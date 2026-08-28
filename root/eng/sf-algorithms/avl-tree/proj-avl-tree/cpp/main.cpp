#include <iostream>
#include <algorithm>
#include <memory>
#include <optional>
#include <initializer_list>

template <typename T>
class AVLTree {
private:
    struct Node {
        T key;
        int height{1};
        std::unique_ptr<Node> left;
        std::unique_ptr<Node> right;

        explicit Node(T val) : key(std::move(val)) {}
    };

    std::unique_ptr<Node> root_;

    static int getHeight(const std::unique_ptr<Node>& node) noexcept {
        return node ? node->height : 0;
    }

    static int getBalance(const std::unique_ptr<Node>& node) noexcept {
        return node ? getHeight(node->right) - getHeight(node->left) : 0;
    }

    static void updateHeight(Node* node) noexcept {
        if (node) {
            node->height = 1 + std::max(getHeight(node->left), getHeight(node->right));
        }
    }

    // Праве обертання (LL-перекіс)
    static std::unique_ptr<Node> rotateRight(std::unique_ptr<Node> y) {
        auto x = std::move(y->left);
        y->left = std::move(x->right);
        updateHeight(y.get());

        x->right = std::move(y);
        updateHeight(x.get());
        return x;
    }

    // Ліве обертання (RR-перекіс)
    static std::unique_ptr<Node> rotateLeft(std::unique_ptr<Node> x) {
        auto y = std::move(x->right);
        x->right = std::move(y->left);
        updateHeight(x.get());

        y->left = std::move(x);
        updateHeight(y.get());
        return y;
    }

    // Відновлення балансу
    static std::unique_ptr<Node> rebalance(std::unique_ptr<Node> node) {
        if (!node) return nullptr;

        updateHeight(node.get());
        int balance = getBalance(node);

        if (balance < -1) {
            if (getBalance(node->left) > 0) {
                node->left = rotateLeft(std::move(node->left));
            }
            return rotateRight(std::move(node));
        }

        if (balance > 1) {
            if (getBalance(node->right) < 0) {
                node->right = rotateRight(std::move(node->right));
            }
            return rotateLeft(std::move(node));
        }

        return node;
    }

    static std::unique_ptr<Node> insertImpl(std::unique_ptr<Node> node, T key) {
        if (!node) {
            return std::make_unique<Node>(std::move(key));
        }

        if (key < node->key) {
            node->left = insertImpl(std::move(node->left), std::move(key));
        } else if (key > node->key) {
            node->right = insertImpl(std::move(node->right), std::move(key));
        } else {
            return node; // Ігноруємо дублікати
        }

        return rebalance(std::move(node));
    }

    static const Node* minNode(const Node* node) noexcept {
        const Node* curr = node;
        while (curr && curr->left) {
            curr = curr->left.get();
        }
        return curr;
    }

    static std::unique_ptr<Node> removeImpl(std::unique_ptr<Node> node, const T& key) {
        if (!node) return nullptr;

        if (key < node->key) {
            node->left = removeImpl(std::move(node->left), key);
        } else if (key > node->key) {
            node->right = removeImpl(std::move(node->right), key);
        } else {
            if (!node->left) return std::move(node->right);
            if (!node->right) return std::move(node->left);

            const Node* successor = minNode(node->right.get());
            node->key = successor->key;
            node->right = removeImpl(std::move(node->right), successor->key);
        }

        return rebalance(std::move(node));
    }

    template <typename Func>
    static void inOrderImpl(const Node* node, Func&& func) {
        if (node) {
            inOrderImpl(node->left.get(), func);
            func(node->key, node->height, getBalance(node));
            inOrderImpl(node->right.get(), func);
        }
    }

public:
    AVLTree() = default;

    AVLTree(std::initializer_list<T> list) {
        for (const auto& item : list) {
            insert(item);
        }
    }

    void insert(T key) {
        root_ = insertImpl(std::move(root_), std::move(key));
    }

    void remove(const T& key) {
        root_ = removeImpl(std::move(root_), key);
    }

    [[nodiscard]] bool contains(const T& key) const noexcept {
        const Node* curr = root_.get();
        while (curr) {
            if (key == curr->key) return true;
            curr = (key < curr->key) ? curr->left.get() : curr->right.get();
        }
        return false;
    }

    template <typename Func>
    void inOrder(Func&& func) const {
        inOrderImpl(root_.get(), std::forward<Func>(func));
    }

    [[nodiscard]] int height() const noexcept {
        return getHeight(root_);
    }
};

int main() {
    AVLTree<int> tree{10, 20, 30, 40, 50, 25};

    std::cout << "In-order обхід (значення, висота, BF):\n";
    tree.inOrder([](int key, int h, int bf) {
        std::cout << key << " (h=" << h << ", bf=" << bf << ") ";
    });
    std::cout << "\n\nВисота дерева: " << tree.height() << "\n";

    std::cout << "Видаляємо 30...\n";
    tree.remove(30);

    std::cout << "Обхід після видалення:\n";
    tree.inOrder([](int key, int h, int bf) {
        std::cout << key << " (h=" << h << ", bf=" << bf << ") ";
    });
    std::cout << "\n";

    return 0;
}
