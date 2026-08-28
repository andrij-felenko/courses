#include <cstdint>
#include <cstddef>
#include <span>
#include <vector>
#include <memory>
#include <bit>
#include <new>

// Блок, вирівняний по 64 байти (кеш-лінія)
struct alignas(64) CacheBlock {
    static constexpr size_t kWords = 8;
    static constexpr size_t kBits = kWords * 64; // 512 бітів
    uint64_t words[kWords]{0};
};

class BlockedBloomFilter {
public:
    explicit BlockedBloomFilter(size_t expected_elements, double fp_rate = 0.01)
        : k_hashes_(8) {
        // Розрахунок кількості блоків з урахуванням дисперсії
        const size_t total_bits = static_cast<size_t>(
            -1.65 * static_cast<double>(expected_elements) * (fp_rate > 0.01 ? -4.6 : -6.9)
        );
        num_blocks_ = (total_bits + CacheBlock::kBits - 1) / CacheBlock::kBits;
        if (num_blocks_ == 0) num_blocks_ = 1;

        // Виділення пам'яті з апаратним вирівнюванням
        blocks_ = std::make_unique_for_overwrite<CacheBlock[]>(num_blocks_);
        std::fill_n(blocks_.get(), num_blocks_, CacheBlock{});
    }

    void add(uint64_t key) noexcept {
        const auto [h1, h2] = compute_hashes(key);
        CacheBlock& block = blocks_[h1 % num_blocks_];

        for (uint32_t i = 0; i < k_hashes_; ++i) {
            const uint32_t bit_idx = (h1 + i * h2) & (CacheBlock::kBits - 1);
            const uint32_t word_idx = bit_idx >> 6;
            const uint64_t bit_mask = 1ULL << (bit_idx & 63);
            block.words[word_idx] |= bit_mask;
        }
    }

    [[nodiscard]] bool contains(uint64_t key) const noexcept {
        const auto [h1, h2] = compute_hashes(key);
        const CacheBlock& block = blocks_[h1 % num_blocks_];

        for (uint32_t i = 0; i < k_hashes_; ++i) {
            const uint32_t bit_idx = (h1 + i * h2) & (CacheBlock::kBits - 1);
            const uint32_t word_idx = bit_idx >> 6;
            const uint64_t bit_mask = 1ULL << (bit_idx & 63);

            if ((block.words[word_idx] & bit_mask) == 0) {
                return false; // 100% відсутній
            }
        }
        return true; // Ймовірно присутній
    }

    [[nodiscard]] size_t memory_bytes() const noexcept {
        return num_blocks_ * sizeof(CacheBlock);
    }

private:
    struct HashPair { uint64_t h1; uint64_t h2; };

    static constexpr HashPair compute_hashes(uint64_t key) noexcept {
        // Швидкий геш SplitMix64
        auto splitmix = [](uint64_t x) constexpr -> uint64_t {
            x ^= x >> 30;
            x *= 0xbf58476d1ce4e5b9ULL;
            x ^= x >> 27;
            x *= 0x94d049bb133111ebULL;
            x ^= x >> 31;
            return x;
        };
        uint64_t h1 = splitmix(key);
        uint64_t h2 = splitmix(h1 ^ 0x517cc1b727220a95ULL);
        return {h1, h2};
    }

    size_t num_blocks_{0};
    uint32_t k_hashes_{8};
    std::unique_ptr<CacheBlock[]> blocks_;
};
