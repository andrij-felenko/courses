using MerkleHash = std::array<uint8_t, MERKLE_HASH_SIZE>;

enum class MerkleDirection {
    Left  = 0,  // Сестра розташована ліворуч від поточного вузла
    Right = 1   // Сестра розташована праворуч від поточного вузла
};

struct MerkleProofNode {
    MerkleHash sibling_hash;
    MerkleDirection direction;
};

using MerkleProof = std::vector<MerkleProofNode>;

class MerkleTree; // Непрозорий клас-контейнер Дерева Меркла (RAII)
