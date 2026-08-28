#include <iostream>
#include <memory>
#include <array>
#include <optional>
#include <algorithm>
#include <utility>

template <typename KeyType>
class Tree234 {
private:
    static constexpr size_t MAX_KEYS = 3;
    static constexpr size_t MAX_CHILDREN = 4;

    struct Node {
        size_t num_keys = 0;
        std::array<KeyType, MAX_KEYS> keys{};
        std::array<std::unique_ptr<Node>, MAX_CHILDREN> children{};

        [[nodiscard]] bool is_leaf() const noexcept {
            return children[0] == nullptr;
        }
    };

    std::unique_ptr<Node> root_;

    /* Превентивне розщеплення дитини parent->children[child_idx] */
    void split_child(Node* parent, size_t child_idx) {
        auto child = parent->children[child_idx].get();
        auto right_sibling = std::make_unique<Node>();

        right_sibling->num_keys = 1;
        right_sibling->keys[0] = std::move(child->keys[2]);

        if (!child->is_leaf()) {
            right_sibling->children[0] = std::move(child->children[2]);
            right_sibling->children[1] = std::move(child->children[3]);
        }

        child->num_keys = 1;

        /* Зсув вказівників у батьківському вузлі */
        for (size_t i = parent->num_keys; i > child_idx; --i) {
            parent->children[i + 1] = std::move(parent->children[i]);
        }
        parent->children[child_idx + 1] = std::move(right_sibling);

        /* Зсув ключів у батьківському вузлі */
        for (size_t i = parent->num_keys; i > child_idx; --i) {
            parent->keys[i] = std::move(parent->keys[i - 1]);
        }
        parent->keys[child_idx] = std::move(child->keys[1]);
        parent->num_keys++;
    }

    /* Вставка у піддерево неповного вузла */
    void insert_non_full(Node* node, KeyType key) {
        int i = static_cast<int>(node->num_keys) - 1;

        if (node->is_leaf()) {
            while (i >= 0 && key < node->keys[i]) {
                node->keys[i + 1] = std::move(node->keys[i]);
                --i;
            }
            node->keys[i + 1] = std::move(key);
            node->num_keys++;
        } else {
            while (i >= 0 && key < node->keys[i]) {
                --i;
            }
            size_t next_idx = static_cast<size_t>(i + 1);

            if (node->children[next_idx]->num_keys == MAX_KEYS) {
                split_child(node, next_idx);
                if (key > node->keys[next_idx]) {
                    next_idx++;
                }
            }
            insert_non_full(node->children[next_idx].get(), std::move(key));
        }
    }

    void print_inorder(const Node* node) const {
        if (!node) return;
        for (size_t i = 0; i < node->num_keys; ++i) {
            print_inorder(node->children[i].get());
            std::cout << node->keys[i] << " ";
        }
        print_inorder(node->children[node->num_keys].get());
    }

public:
    Tree234() = default;
    ~Tree234() = default;

    /* Заборона копіювання, дозвіл переміщення */
    Tree234(Tree234&&) noexcept = default;
    Tree234& operator=(Tree234&&) noexcept = default;
    Tree234(const Tree234&) = delete;
    Tree234& operator=(const Tree234&) = delete;

    /* Вставка нового ключа */
    void insert(KeyType key) {
        if (!root_) {
            root_ = std::make_unique<Node>();
            root_->keys[0] = std::move(key);
            root_->num_keys = 1;
            return;
        }

        if (root_->num_keys == MAX_KEYS) {
            auto new_root = std::make_unique<Node>();
            new_root->children[0] = std::move(root_);
            split_child(new_root.get(), 0);
            root_ = std::move(new_root);
        }

        insert_non_full(root_.get(), std::move(key));
    }

    /* Пошук ключа за константний час на рівень */
    [[nodiscard]] bool contains(const KeyType& key) const noexcept {
        const Node* curr = root_.get();
        while (curr != nullptr) {
            size_t i = 0;
            while (i < curr->num_keys && key > curr->keys[i]) {
                ++i;
            }
            if (i < curr->num_keys && key == curr->keys[i]) {
                return true;
            }
            if (curr->is_leaf()) {
                break;
            }
            curr = curr->children[i].get();
        }
        return false;
    }

    /* Вивід відсортованого вмісту */
    void print() const {
        print_inorder(root_.get());
        std::cout << "\n";
    }
};
