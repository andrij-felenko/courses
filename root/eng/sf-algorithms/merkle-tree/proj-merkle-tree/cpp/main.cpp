#include <iostream>
#include <vector>
#include <string_view>
#include <array>
#include <memory>
#include <algorithm>
#include <iomanip>

namespace crypto {

constexpr size_t HASH_SIZE = 32;
constexpr uint8_t PREFIX_LEAF = 0x00;
constexpr uint8_t PREFIX_INTERNAL = 0x01;

using HashBytes = std::array<uint8_t, HASH_SIZE>;

enum class Direction { Left, Right };

struct ProofNode {
    HashBytes sibling_hash;
    Direction direction;
};

using MerkleProof = std::vector<ProofNode>;

/* Реалізація FNV-1a 256-біт для демонстрації */
inline HashBytes compute_hash(uint8_t prefix, std::string_view data) {
    HashBytes result{};
    result.fill(0x81);
    
    for (size_t i = 0; i < HASH_SIZE; ++i) {
        result[i] ^= prefix;
        result[i] *= 16777619u;
    }
    
    for (size_t i = 0; i < data.size(); ++i) {
        result[i % HASH_SIZE] ^= static_cast<uint8_t>(data[i]);
        result[i % HASH_SIZE] *= 16777619u;
    }
    return result;
}

inline HashBytes combine_hashes(const HashBytes& left, const HashBytes& right) {
    std::array<uint8_t, HASH_SIZE * 2> buffer{};
    std::copy(left.begin(), left.end(), buffer.begin());
    std::copy(right.begin(), right.end(), buffer.begin() + HASH_SIZE);
    return compute_hash(PREFIX_INTERNAL, std::string_view(reinterpret_cast<const char*>(buffer.data()), buffer.size()));
}

class MerkleTree {
public:
    explicit MerkleTree(std::span<const std::string_view> items) : leaf_count_(items.size()) {
        if (items.empty()) return;
        
        // Крок 1: Створення листків
        std::vector<HashBytes> current_level;
        current_level.reserve(items.size());
        for (const auto& item : items) {
            current_level.push_back(compute_hash(PREFIX_LEAF, item));
        }
        
        levels_.push_back(current_level);
        
        // Крок 2: Побудова вищих рівнів
        while (current_level.size() > 1) {
            std::vector<HashBytes> next_level;
            next_level.reserve((current_level.size() + 1) / 2);
            
            for (size_t i = 0; i < current_level.size(); i += 2) {
                const auto& left = current_level[i];
                const auto& right = (i + 1 < current_level.size()) ? current_level[i + 1] : left;
                next_level.push_back(combine_hashes(left, right));
            }
            
            levels_.push_back(next_level);
            current_level = std::move(next_level);
        }
    }

    [[nodiscard]] HashBytes root() const {
        if (levels_.empty() || levels_.back().empty()) return {};
        return levels_.back().front();
    }

    [[nodiscard]] MerkleProof prove(size_t index) const {
        MerkleProof proof;
        if (index >= leaf_count_ || levels_.empty()) return proof;

        size_t current_idx = index;
        for (size_t level = 0; level < levels_.size() - 1; ++level) {
            const auto& current_level = levels_[level];
            size_t sibling_idx;
            Direction dir;

            if (current_idx % 2 == 0) {
                sibling_idx = (current_idx + 1 < current_level.size()) ? current_idx + 1 : current_idx;
                dir = Direction::Right;
            } else {
                sibling_idx = current_idx - 1;
                dir = Direction::Left;
            }

            proof.push_back(ProofNode{
                .sibling_hash = current_level[sibling_idx],
                .direction = dir
            });

            current_idx /= 2;
        }

        return proof;
    }

    static bool verify(std::string_view item, const MerkleProof& proof, const HashBytes& expected_root) {
        HashBytes current = compute_hash(PREFIX_LEAF, item);

        for (const auto& node : proof) {
            if (node.direction == Direction::Right) {
                current = combine_hashes(current, node.sibling_hash);
            } else {
                current = combine_hashes(node.sibling_hash, current);
            }
        }

        return current == expected_root;
    }

private:
    size_t leaf_count_{0};
    std::vector<std::vector<HashBytes>> levels_;
};

} // namespace crypto

int main() {
    const std::vector<std::string_view> txs = {
        "Tx1: Alice->Bob 5 BTC",
        "Tx2: Bob->Charlie 2 BTC",
        "Tx3: Charlie->Dave 1 BTC",
        "Tx4: Dave->Eve 0.5 BTC"
    };

    crypto::MerkleTree tree(txs);
    auto root = tree.root();

    std::cout << "Merkle Root: ";
    for (size_t i = 0; i < 8; ++i) {
        std::cout << std::hex << std::setw(2) << std::setfill('0') << static_cast<int>(root[i]);
    }
    std::cout << "...\n";

    // Перевірка індексу 1 (Tx2)
    auto proof = tree.prove(1);
    bool is_valid = crypto::MerkleTree::verify(txs[1], proof, root);
    std::cout << "Перевірка Tx2: " << (is_valid ? "УСПІШНО (VALID)" : "ПОМИЛКА") << "\n";

    bool is_fake_valid = crypto::MerkleTree::verify("Tx2: Bob->Charlie 999 BTC", proof, root);
    std::cout << "Підроблена Tx2: " << (is_fake_valid ? "УСПІШНО" : "ВІДХИЛЕНО (INVALID)") << "\n";

    return 0;
}
