// Арена-виділювач пам'яті у C++ з використанням std::vector як хранилища
class TreeArenaCPP {
private:
    struct RawNode {
        int data;
        RawNode* left = nullptr;
        RawNode* right = nullptr;
    };
    std::vector<std::vector<RawNode>> chunks;
    size_t chunk_size;
    size_t current_chunk_idx = 0;
    size_t current_node_idx = 0;

public:
    explicit TreeArenaCPP(size_t chunkSize = 4096) : chunk_size(chunkSize) {
        chunks.emplace_back(chunk_size);
    }

    RawNode* alloc(int val) {
        if (current_node_idx >= chunk_size) {
            chunks.emplace_back(chunk_size);
            current_chunk_idx++;
            current_node_idx = 0;
        }
        RawNode* node = &chunks[current_chunk_idx][current_node_idx++];
        node->data = val;
        node->left = nullptr;
        node->right = nullptr;
        return node;
    }
    // Вся пам'ять усіх блоків звільняється автоматично в деструкторі std::vector
};
