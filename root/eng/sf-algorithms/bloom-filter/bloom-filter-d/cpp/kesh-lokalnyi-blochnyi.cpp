#include <cstdint>
#include <vector>
#include <cstddef>
#include <new>

class blocked_bloom_filter {
public:
    struct alignas(64) cache_block {
        std::uint32_t buckets[16]{0}; // 64 байти
    };

    explicit blocked_bloom_filter(std::size_t num_blocks)
        : num_blocks_(num_blocks), blocks_(num_blocks) {}

    [[nodiscard]] bool check(std::uint64_t h1, std::uint64_t h2) const noexcept {
        std::size_t block_idx = h1 % num_blocks_;
        const auto& block = blocks_[block_idx];

        for (std::size_t i = 0; i < 8; ++i) {
            std::uint32_t bit_idx = static_cast<std::uint32_t>((h2 + i * 0x9e3779b9u) & 511);
            std::uint32_t bucket = block.buckets[bit_idx >> 5];
            if ((bucket & (1u << (bit_idx & 31))) == 0) {
                return false;
            }
        }
        return true;
    }

private:
    std::size_t num_blocks_;
    std::vector<cache_block> blocks_;
};
