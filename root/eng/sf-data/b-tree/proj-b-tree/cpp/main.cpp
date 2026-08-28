#include <iostream>
#include <vector>
#include <memory>
#include <optional>
#include <algorithm>

template <typename T, std::size_t MinDegree = 3>
class BTree {
    static_assert(MinDegree >= 2, "Мінімальний ступінь MinDegree має бути >= 2");
    static constexpr std::size_t MaxKeys = 2 * MinDegree - 1;
    static constexpr std::size_t MaxChildren = 2 * MinDegree;

    struct Node {
        std::vector<T> keys;
        std::vector<std::unique_ptr<Node>> children;
        bool is_leaf{true};

        explicit Node(bool leaf) : is_leaf(leaf) {
            keys.reserve(MaxKeys);
            if (!is_leaf) {
                children.reserve(MaxChildren);
            }
        }

        [[nodiscard]] bool is_full() const noexcept {
            return keys.size() == MaxKeys;
        }
    };

    std::unique_ptr<Node> root_;

    void split_child(Node* parent, std::size_t idx) {
        auto full_child = parent->children[idx].get();
        auto new_child = std::make_unique<Node>(full_child->is_leaf);

        // Переміщуємо останні (MinDegree - 1) ключів до нового вузла
        auto mid_it = full_child->keys.begin() + MinDegree;
        new_child->keys.assign(
            std::make_move_iterator(mid_it),
            std::make_move_iterator(full_child->keys.end())
        );

        // Якщо вузол внутрішній — переміщуємо відповідні дочірні вказівники
        if (!full_child->is_leaf) {
            auto child_mid_it = full_child->children.begin() + MinDegree;
            new_child->children.assign(
                std::make_move_iterator(child_mid_it),
                std::make_move_iterator(full_child->children.end())
            );
            full_child->children.erase(child_mid_it, full_child->children.end());
        }

        // Забираємо медіанний ключ для підйому до батька
        T median_key = std::move(full_child->keys[MinDegree - 1]);
        full_child->keys.erase(full_child->keys.begin() + (MinDegree - 1), full_child->keys.end());

        // Вставляємо новий дочірній вузол у вектор дітей батька
        parent->children.insert(parent->children.begin() + idx + 1, std::move(new_child));

        // Вставляємо медіанний ключ у батьківський вузол
        parent->keys.insert(parent->keys.begin() + idx, std::move(median_key));
    }

    void insert_non_full(Node* node, T key) {
        if (node->is_leaf) {
            auto pos = std::upper_bound(node->keys.begin(), node->keys.end(), key);
            node->keys.insert(pos, std::move(key));
        } else {
            auto it = std::upper_bound(node->keys.begin(), node->keys.end(), key);
            std::size_t idx = std::distance(node->keys.begin(), it);

            if (node->children[idx]->is_full()) {
                split_child(node, idx);
                if (key > node->keys[idx]) {
                    idx++;
                }
            }
            insert_non_full(node->children[idx].get(), std::move(key));
        }
    }

    void traverse_impl(const Node* node) const {
        if (!node) return;
        std::size_t i = 0;
        for (i = 0; i < node->keys.size(); ++i) {
            if (!node->is_leaf) {
                traverse_impl(node->children[i].get());
            }
            std::cout << node->keys[i] << " ";
        }
        if (!node->is_leaf) {
            traverse_impl(node->children[i].get());
        }
    }

public:
    BTree() : root_(std::make_unique<Node>(true)) {}

    void insert(T key) {
        if (root_->is_full()) {
            auto new_root = std::make_unique<Node>(false);
            new_root->children.push_back(std::move(root_));
            split_child(new_root.get(), 0);
            root_ = std::move(new_root);
        }
        insert_non_full(root_.get(), std::move(key));
    }

    [[nodiscard]] bool contains(const T& key) const noexcept {
        const Node* curr = root_.get();
        while (curr) {
            auto it = std::lower_bound(curr->keys.begin(), curr->keys.end(), key);
            if (it != curr->keys.end() && *it == key) {
                return true;
            }
            if (curr->is_leaf) {
                return false;
            }
            std::size_t idx = std::distance(curr->keys.begin(), it);
            curr = curr->children[idx].get();
        }
        return false;
    }

    void traverse() const {
        traverse_impl(root_.get());
        std::cout << "\n";
    }
};

int main() {
    BTree<int, 3> tree;
    std::vector<int> keys = {10, 20, 5, 6, 12, 30, 7, 17, 3, 22, 27, 45, 1, 35};

    for (int k : keys) {
        tree.insert(k);
    }

    std::cout << "Обхід B-дерева у C++ (std::unique_ptr & RAII):\n";
    tree.traverse();

    int search_key = 17;
    if (tree.contains(search_key)) {
        std::cout << "Ключ " << search_key << " знайдено у B-дереві\n";
    } else {
        std::cout << "Ключ " << search_key << " відсутній у B-дереві\n";
    }

    return 0;
}
