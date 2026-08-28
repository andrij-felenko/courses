#include <iostream>
#include <vector>
#include <memory>
#include <optional>
#include <algorithm>
#include <span>
#include <cstdint>

struct TupleId {
    uint32_t page_id{0};
    uint16_t offset{0};

    auto operator<=>(const TupleId&) const = default;
};

template <typename Key = int64_t, typename Value = TupleId, size_t Order = 4>
class BPlusTree {
    static_assert(Order >= 3, "Порядок B+дерева повинен бути щонайменше 3");

    struct Node {
        bool is_leaf{true};
        std::vector<Key> keys;
        Node* parent{nullptr};

        explicit Node(bool leaf) : is_leaf(leaf) {
            keys.reserve(Order + 1);
        }
        virtual ~Node() = default;
    };

    struct LeafNode : public Node {
        std::vector<Value> values;
        LeafNode* next{nullptr};

        LeafNode() : Node(true) {
            values.reserve(Order + 1);
        }
    };

    struct InternalNode : public Node {
        std::vector<std::unique_ptr<Node>> children;

        InternalNode() : Node(false) {
            children.reserve(Order + 2);
        }
    };

    std::unique_ptr<Node> root_;

    LeafNode* find_leaf(Node* current, const Key& key) const {
        if (!current) return nullptr;
        if (current->is_leaf) {
            return static_cast<LeafNode*>(current);
        }
        auto* internal = static_cast<InternalNode*>(current);
        auto it = std::upper_bound(internal->keys.begin(), internal->keys.end(), key);
        size_t idx = std::distance(internal->keys.begin(), it);
        return find_leaf(internal->children[idx].get(), key);
    }

    void insert_into_parent(Node* left, Key key, std::unique_ptr<Node> right) {
        Node* parent_ptr = left->parent;
        if (!parent_ptr) {
            auto new_root = std::make_unique<InternalNode>();
            new_root->keys.push_back(key);
            left->parent = new_root.get();
            right->parent = new_root.get();

            new_root->children.push_back(std::move(root_));
            new_root->children.push_back(std::move(right));
            root_ = std::move(new_root);
            return;
        }

        auto* parent = static_cast<InternalNode*>(parent_ptr);
        auto it_key = std::upper_bound(parent->keys.begin(), parent->keys.end(), key);
        size_t idx = std::distance(parent->keys.begin(), it_key);

        parent->keys.insert(it_key, key);
        right->parent = parent;
        parent->children.insert(parent->children.begin() + idx + 1, std::move(right));

        if (parent->keys.size() >= Order) {
            split_internal(parent);
        }
    }

    void split_internal(InternalNode* node) {
        auto new_node = std::make_unique<InternalNode>();
        size_t split_idx = node->keys.size() / 2;
        Key promote_key = node->keys[split_idx];

        new_node->keys.assign(node->keys.begin() + split_idx + 1, node->keys.end());
        node->keys.erase(node->keys.begin() + split_idx, node->keys.end());

        for (size_t i = split_idx + 1; i < node->children.size(); ++i) {
            node->children[i]->parent = new_node.get();
            new_node->children.push_back(std::move(node->children[i]));
        }
        node->children.erase(node->children.begin() + split_idx + 1, node->children.end());

        insert_into_parent(node, promote_key, std::move(new_node));
    }

    void split_leaf(LeafNode* leaf, Key key, Value val) {
        auto it = std::lower_bound(leaf->keys.begin(), leaf->keys.end(), key);
        size_t idx = std::distance(leaf->keys.begin(), it);
        leaf->keys.insert(it, key);
        leaf->values.insert(leaf->values.begin() + idx, val);

        auto new_leaf = std::make_unique<LeafNode>();
        size_t split_idx = leaf->keys.size() / 2;

        new_leaf->keys.assign(leaf->keys.begin() + split_idx, leaf->keys.end());
        new_leaf->values.assign(leaf->values.begin() + split_idx, leaf->values.end());

        leaf->keys.erase(leaf->keys.begin() + split_idx, leaf->keys.end());
        leaf->values.erase(leaf->values.begin() + split_idx, leaf->values.end());

        new_leaf->next = leaf->next;
        leaf->next = new_leaf.get();

        Key promote_key = new_leaf->keys.front();
        insert_into_parent(leaf, promote_key, std::move(new_leaf));
    }

public:
    BPlusTree() = default;

    [[nodiscard]] std::optional<Value> find(const Key& key) const {
        LeafNode* leaf = find_leaf(root_.get(), key);
        if (!leaf) return std::nullopt;

        auto it = std::lower_bound(leaf->keys.begin(), leaf->keys.end(), key);
        if (it != leaf->keys.end() && *it == key) {
            size_t idx = std::distance(leaf->keys.begin(), it);
            return leaf->values[idx];
        }
        return std::nullopt;
    }

    [[nodiscard]] std::vector<Value> range_scan(const Key& min_key, const Key& max_key) const {
        std::vector<Value> result;
        LeafNode* leaf = find_leaf(root_.get(), min_key);

        while (leaf) {
            for (size_t i = 0; i < leaf->keys.size(); ++i) {
                if (leaf->keys[i] >= min_key && leaf->keys[i] <= max_key) {
                    result.push_back(leaf->values[i]);
                } else if (leaf->keys[i] > max_key) {
                    return result;
                }
            }
            leaf = leaf->next;
        }
        return result;
    }

    void insert(Key key, Value val) {
        if (!root_) {
            auto leaf = std::make_unique<LeafNode>();
            leaf->keys.push_back(key);
            leaf->values.push_back(val);
            root_ = std::move(leaf);
            return;
        }

        LeafNode* leaf = find_leaf(root_.get(), key);
        if (leaf->keys.size() < Order - 1) {
            auto it = std::lower_bound(leaf->keys.begin(), leaf->keys.end(), key);
            size_t idx = std::distance(leaf->keys.begin(), it);
            leaf->keys.insert(it, key);
            leaf->values.insert(leaf->values.begin() + idx, val);
            return;
        }

        split_leaf(leaf, key, val);
    }
};
