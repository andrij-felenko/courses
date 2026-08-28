#include <iostream>
#include <vector>
#include <array>
#include <string>
#include <string_view>
#include <cstdint>
#include <iomanip>

namespace storage {

constexpr size_t MerkleDepth = 3;
constexpr size_t NumLeaves = 1ULL << MerkleDepth;
constexpr size_t TreeSize = 1ULL << (MerkleDepth + 1);

constexpr uint64_t FnvOffset = 14695981039346656037ULL;
constexpr uint64_t FnvPrime  = 1099511628211ULL;

[[nodiscard]] constexpr uint64_t fnv1a(std::string_view data) noexcept {
    uint64_t hash = FnvOffset;
    for (char c : data) {
        hash ^= static_cast<uint8_t>(c);
        hash *= FnvPrime;
    }
    return hash;
}

[[nodiscard]] constexpr uint64_t fnv1a_combine(uint64_t left, uint64_t right) noexcept {
    uint64_t hash = FnvOffset;
    hash ^= left;  hash *= FnvPrime;
    hash ^= right; hash *= FnvPrime;
    return hash;
}

struct Record {
    uint64_t key_token;
    std::string key;
    std::string value;
    uint64_t timestamp;
    bool is_tombstone{false};

    [[nodiscard]] uint64_t hash() const noexcept {
        uint64_t h = fnv1a(key);
        h = fnv1a_combine(h, fnv1a(value));
        h = fnv1a_combine(h, timestamp);
        h = fnv1a_combine(h, static_cast<uint64_t>(is_tombstone));
        return h;
    }
};

class MerkleTree {
public:
    MerkleTree() {
        nodes_.fill(0);
        leaf_counts_.fill(0);
    }

    void add_record(const Record& rec) noexcept {
        const size_t leaf_idx = static_cast<size_t>(rec.key_token >> (64 - MerkleDepth));
        const size_t node_idx = NumLeaves + leaf_idx;

        const uint64_t h = rec.hash();
        if (leaf_counts_[leaf_idx] == 0) {
            nodes_[node_idx] = h;
        } else {
            nodes_[node_idx] = fnv1a_combine(nodes_[node_idx], h);
        }
        leaf_counts_[leaf_idx]++;
    }

    void build() noexcept {
        for (size_t i = NumLeaves - 1; i >= 1; --i) {
            const uint64_t left = nodes_[2 * i];
            const uint64_t right = nodes_[2 * i + 1];
            if (left == 0 && right == 0) {
                nodes_[i] = 0;
            } else {
                nodes_[i] = fnv1a_combine(left, right);
            }
        }
    }

    [[nodiscard]] uint64_t root() const noexcept {
        return nodes_[1];
    }

    [[nodiscard]] static std::vector<size_t> find_differences(
        const MerkleTree& a, const MerkleTree& b) {
        std::vector<size_t> diff_leaves;
        diff_leaves.reserve(NumLeaves);
        find_diffs_recursive(a, b, 1, 0, diff_leaves);
        return diff_leaves;
    }

private:
    static void find_diffs_recursive(
        const MerkleTree& a, const MerkleTree& b,
        size_t node_idx, size_t depth,
        std::vector<size_t>& diffs) {
        if (a.nodes_[node_idx] == b.nodes_[node_idx]) {
            return;
        }

        if (depth == MerkleDepth) {
            diffs.push_back(node_idx - NumLeaves);
            return;
        }

        find_diffs_recursive(a, b, 2 * node_idx, depth + 1, diffs);
        find_diffs_recursive(a, b, 2 * node_idx + 1, depth + 1, diffs);
    }

    std::array<uint64_t, TreeSize> nodes_;
    std::array<size_t, NumLeaves> leaf_counts_;
};

} // namespace storage

int main() {
    using namespace storage;

    MerkleTree node_a;
    MerkleTree node_b;

    const Record r1{ 0x1000000000000000ULL, "user:101", "Alice", 1000, false };
    const Record r2{ 0x4000000000000000ULL, "user:102", "Bob",   1000, false };
    const Record r3{ 0x8000000000000000ULL, "user:103", "Carol", 1000, false };

    node_a.add_record(r1); node_a.add_record(r2); node_a.add_record(r3);
    node_b.add_record(r1); node_b.add_record(r2); node_b.add_record(r3);

    const Record r4{ 0xC000000000000000ULL, "user:104", "Dave_Updated", 2000, false };
    node_a.add_record(r4);

    node_a.build();
    node_b.build();

    std::cout << std::hex << std::uppercase << std::setfill('0');
    std::cout << "Корінь Репліки A: 0x" << std::setw(16) << node_a.root() << "\n";
    std::cout << "Корінь Репліки B: 0x" << std::setw(16) << node_b.root() << "\n";

    const auto diffs = MerkleTree::find_differences(node_a, node_b);
    std::cout << std::dec << "Знайдено розбіжних листків: " << diffs.size() << "\n";

    for (size_t leaf : diffs) {
        const uint64_t range_start = static_cast<uint64_t>(leaf) << (64 - MerkleDepth);
        const uint64_t range_end = range_start + (1ULL << (64 - MerkleDepth)) - 1;
        std::cout << "  -> Листок " << leaf << ": діапазон токенів [0x"
                  << std::hex << std::setw(16) << range_start << ", 0x"
                  << std::setw(16) << range_end << "]\n" << std::dec;
    }

    return 0;
}
