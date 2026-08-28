#include <iostream>
#include <memory>
#include <string>
#include <vector>
#include <optional>
#include <cstdint>
#include <bit>

// Незмінне персистентне HAMT-дерево мовою C++20
class PersistentHAMT {
public:
    using Key = std::string;
    using Value = int;

private:
    static constexpr std::uint32_t BITS_PER_LEVEL = 5;
    static constexpr std::uint32_t BITMAP_MASK = 0x1F;

    static std::uint32_t fnv1a_hash(std::string_view key) noexcept {
        std::uint32_t hash = 2166136261U;
        for (char ch : key) {
            hash ^= static_cast<std::uint8_t>(ch);
            hash *= 16777619U;
        }
        return hash;
    }

    struct Node;
    using NodePtr = std::shared_ptr<const Node>;

    struct LeafData {
        Key key;
        std::uint32_t hash;
        Value value;
    };

    struct BitmapData {
        std::uint32_t bitmap{0};
        std::vector<NodePtr> children;
    };

    struct Node {
        enum class Type { Leaf, Bitmap } type;
        std::optional<LeafData> leaf;
        std::optional<BitmapData> bitmap_node;

        static NodePtr make_leaf(Key key, std::uint32_t hash, Value val) {
            auto n = std::make_shared<Node>();
            n->type = Type::Leaf;
            n->leaf = LeafData{std::move(key), hash, val};
            return n;
        }

        static NodePtr make_bitmap(std::uint32_t bmp, std::vector<NodePtr> children) {
            auto n = std::make_shared<Node>();
            n->type = Type::Bitmap;
            n->bitmap_node = BitmapData{bmp, std::move(children)};
            return n;
        }
    };

    NodePtr root_;

    static NodePtr insert_rec(const NodePtr& node, const Key& key, std::uint32_t hash, Value val, std::uint32_t shift) {
        if (!node) {
            return Node::make_leaf(key, hash, val);
        }

        if (node->type == Node::Type::Leaf) {
            const auto& leaf = *node->leaf;
            if (leaf.hash == hash && leaf.key == key) {
                return Node::make_leaf(key, hash, val);
            }

            std::uint32_t existing_chunk = (leaf.hash >> shift) & BITMAP_MASK;
            std::uint32_t new_chunk = (hash >> shift) & BITMAP_MASK;

            if (existing_chunk == new_chunk) {
                auto sub_node = insert_rec(node, key, hash, val, shift + BITS_PER_LEVEL);
                return Node::make_bitmap(1U << existing_chunk, {sub_node});
            } else {
                auto new_leaf = Node::make_leaf(key, hash, val);
                auto existing_leaf = Node::make_leaf(leaf.key, leaf.hash, leaf.value);
                std::uint32_t bmp = (1U << existing_chunk) | (1U << new_chunk);

                if (existing_chunk < new_chunk) {
                    return Node::make_bitmap(bmp, {existing_leaf, new_leaf});
                } else {
                    return Node::make_bitmap(bmp, {new_leaf, existing_leaf});
                }
            }
        }

        const auto& bnode = *node->bitmap_node;
        std::uint32_t chunk = (hash >> shift) & BITMAP_MASK;
        std::uint32_t bit_pos = 1U << chunk;
        std::uint32_t bmp = bnode.bitmap;

        if ((bmp & bit_pos) != 0) {
            std::size_t idx = std::popcount(bmp & (bit_pos - 1));
            auto updated_child = insert_rec(bnode.children[idx], key, hash, val, shift + BITS_PER_LEVEL);

            std::vector<NodePtr> new_children = bnode.children;
            new_children[idx] = updated_child;
            return Node::make_bitmap(bmp, std::move(new_children));
        } else {
            auto new_leaf = Node::make_leaf(key, hash, val);
            std::uint32_t new_bmp = bmp | bit_pos;
            std::size_t idx = std::popcount(bmp & (bit_pos - 1));

            std::vector<NodePtr> new_children = bnode.children;
            new_children.insert(new_children.begin() + idx, new_leaf);
            return Node::make_bitmap(new_bmp, std::move(new_children));
        }
    }

    explicit PersistentHAMT(NodePtr root) : root_(std::move(root)) {}

public:
    PersistentHAMT() = default;

    [[nodiscard]] PersistentHAMT insert(const Key& key, Value val) const {
        std::uint32_t hash = fnv1a_hash(key);
        return PersistentHAMT(insert_rec(root_, key, hash, val, 0));
    }

    [[nodiscard]] std::optional<Value> lookup(std::string_view key) const {
        if (!root_) return std::nullopt;
        std::uint32_t hash = fnv1a_hash(key);
        NodePtr curr = root_;
        std::uint32_t shift = 0;

        while (curr) {
            if (curr->type == Node::Type::Leaf) {
                const auto& leaf = *curr->leaf;
                if (leaf.hash == hash && leaf.key == key) {
                    return leaf.value;
                }
                return std::nullopt;
            }

            const auto& bnode = *curr->bitmap_node;
            std::uint32_t chunk = (hash >> shift) & BITMAP_MASK;
            std::uint32_t bit_pos = 1U << chunk;

            if ((bnode.bitmap & bit_pos) == 0) {
                return std::nullopt;
            }

            std::size_t idx = std::popcount(bnode.bitmap & (bit_pos - 1));
            curr = bnode.children[idx];
            shift += BITS_PER_LEVEL;
        }
        return std::nullopt;
    }
};

int main() {
    PersistentHAMT v1;
    v1 = v1.insert("alpha", 100);
    v1 = v1.insert("beta", 200);

    PersistentHAMT v2 = v1.insert("alpha", 999);

    if (auto val = v1.lookup("alpha")) {
        std::cout << "V1 ['alpha'] = " << *val << " (очікується 100)\n";
    }
    if (auto val = v2.lookup("alpha")) {
        std::cout << "V2 ['alpha'] = " << *val << " (очікується 999)\n";
    }
    return 0;
}
