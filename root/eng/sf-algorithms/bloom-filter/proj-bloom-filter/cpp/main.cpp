#include <vector>
#include <string_view>
#include <cmath>
#include <cstdint>
#include <cstddef>
#include <stdexcept>
#include <algorithm>

namespace sys {

class bloom_filter {
public:
    // Створення з явними параметрами m та k
    bloom_filter(std::size_t num_bits, std::size_t num_hashes)
        : num_bits_(num_bits), num_hashes_(num_hashes), item_count_(0) {
        if (num_bits == 0 || num_hashes == 0) {
            throw std::invalid_argument("Розмір масиву та кількість хешів повинні бути більші за 0");
        }
        std::size_t byte_count = (num_bits + 7) / 8;
        bits_.resize(byte_count, 0);
    }

    // Автоматичний розрахунок m та k за очікуваною кількістю n та помилкою p
    bloom_filter(std::size_t expected_items, double false_positive_rate)
        : item_count_(0) {
        if (expected_items == 0 || false_positive_rate <= 0.0 || false_positive_rate >= 1.0) {
            throw std::invalid_argument("Некоректні параметри створення фільтра Блума");
        }

        double num_bits_d = -((double)expected_items * std::log(false_positive_rate)) / 
                            (std::log(2.0) * std::log(2.0));
        num_bits_ = static_cast<std::size_t>(std::ceil(num_bits_d));

        double num_hashes_d = (static_cast<double>(num_bits_) / expected_items) * std::log(2.0);
        num_hashes_ = std::max<std::size_t>(1, static_cast<std::size_t>(std::round(num_hashes_d)));

        std::size_t byte_count = (num_bits_ + 7) / 8;
        bits_.resize(byte_count, 0);
    }

    void insert(std::string_view key) {
        if (key.empty()) return;
        auto [h1, h2] = murmurhash3_x64_128(key.data(), key.size(), 0x9773b15d);

        for (std::size_t i = 0; i < num_hashes_; ++i) {
            std::size_t bit_index = (h1 + i * h2) % num_bits_;
            bits_[bit_index >> 3] |= static_cast<uint8_t>(1u << (bit_index & 7));
        }
        ++item_count_;
    }

    [[nodiscard]] bool contains(std::string_view key) const {
        if (key.empty()) return false;
        auto [h1, h2] = murmurhash3_x64_128(key.data(), key.size(), 0x9773b15d);

        for (std::size_t i = 0; i < num_hashes_; ++i) {
            std::size_t bit_index = (h1 + i * h2) % num_bits_;
            if (!(bits_[bit_index >> 3] & (1u << (bit_index & 7)))) {
                return false;
            }
        }
        return true;
    }

    void clear() noexcept {
        std::fill(bits_.begin(), bits_.end(), static_cast<uint8_t>(0));
        item_count_ = 0;
    }

    [[nodiscard]] double current_false_positive_rate() const noexcept {
        if (num_bits_ == 0) return 1.0;
        double kn = static_cast<double>(num_hashes_ * item_count_);
        double m = static_cast<double>(num_bits_);
        return std::pow(1.0 - std::exp(-kn / m), static_cast<double>(num_hashes_));
    }

    [[nodiscard]] std::size_t size_in_bits() const noexcept { return num_bits_; }
    [[nodiscard]] std::size_t hash_count() const noexcept { return num_hashes_; }
    [[nodiscard]] std::size_t item_count() const noexcept { return item_count_; }
    [[nodiscard]] std::size_t memory_bytes() const noexcept { return bits_.size(); }

private:
    struct hash_pair {
        std::size_t h1;
        std::size_t h2;
    };

    static inline uint64_t rotl64(uint64_t x, int8_t r) noexcept {
        return (x << r) | (x >> (64 - r));
    }

    static hash_pair murmurhash3_x64_128(const void *key, std::size_t len, uint32_t seed) noexcept {
        const auto *data = static_cast<const uint8_t *>(key);
        const std::size_t nblocks = len / 16;

        uint64_t h1 = seed;
        uint64_t h2 = seed;

        constexpr uint64_t c1 = 0x87c37b91114253d5ULL;
        constexpr uint64_t c2 = 0x4cf5ad432745937fULL;

        const auto *blocks = static_cast<const uint64_t *>(key);

        for (std::size_t i = 0; i < nblocks; ++i) {
            uint64_t k1 = blocks[i * 2];
            uint64_t k2 = blocks[i * 2 + 1];

            k1 *= c1; k1 = rotl64(k1, 31); k1 *= c2; h1 ^= k1;
            h1 = rotl64(h1, 27); h1 += h2; h1 = h1 * 5 + 0x52dce729;

            k2 *= c2; k2 = rotl64(k2, 33); k2 *= c1; h2 ^= k2;
            h2 = rotl64(h2, 31); h2 += h1; h2 = h2 * 5 + 0x38495ab5;
        }

        const auto *tail = data + nblocks * 16;
        uint64_t k1 = 0;
        uint64_t k2 = 0;

        switch (len & 15) {
            case 15: k2 ^= static_cast<uint64_t>(tail[14]) << 48; [[fallthrough]];
            case 14: k2 ^= static_cast<uint64_t>(tail[13]) << 40; [[fallthrough]];
            case 13: k2 ^= static_cast<uint64_t>(tail[12]) << 32; [[fallthrough]];
            case 12: k2 ^= static_cast<uint64_t>(tail[11]) << 24; [[fallthrough]];
            case 11: k2 ^= static_cast<uint64_t>(tail[10]) << 16; [[fallthrough]];
            case 10: k2 ^= static_cast<uint64_t>(tail[9]) << 8;   [[fallthrough]];
            case  9: k2 ^= static_cast<uint64_t>(tail[8]);
                     k2 *= c2; k2 = rotl64(k2, 33); k2 *= c1; h2 ^= k2; [[fallthrough]];
            case  8: k1 ^= static_cast<uint64_t>(tail[7]) << 56; [[fallthrough]];
            case  7: k1 ^= static_cast<uint64_t>(tail[6]) << 48; [[fallthrough]];
            case  6: k1 ^= static_cast<uint64_t>(tail[5]) << 40; [[fallthrough]];
            case  5: k1 ^= static_cast<uint64_t>(tail[4]) << 32; [[fallthrough]];
            case  4: k1 ^= static_cast<uint64_t>(tail[3]) << 24; [[fallthrough]];
            case  3: k1 ^= static_cast<uint64_t>(tail[2]) << 16; [[fallthrough]];
            case  2: k1 ^= static_cast<uint64_t>(tail[1]) << 8;  [[fallthrough]];
            case  1: k1 ^= static_cast<uint64_t>(tail[0]);
                     k1 *= c1; k1 = rotl64(k1, 31); k1 *= c2; h1 ^= k1;
        }

        h1 ^= len; h2 ^= len;
        h1 += h2; h2 += h1;

        h1 ^= h1 >> 33; h1 *= 0xff51afd7ed558ccdULL;
        h1 ^= h1 >> 33; h1 *= 0xc4ceb9fe1a85ec53ULL;
        h1 ^= h1 >> 33;

        h2 ^= h2 >> 33; h2 *= 0xff51afd7ed558ccdULL;
        h2 ^= h2 >> 33; h2 *= 0xc4ceb9fe1a85ec53ULL;
        h2 ^= h2 >> 33;

        h1 += h2; h2 += h1;

        return {static_cast<std::size_t>(h1), static_cast<std::size_t>(h2)};
    }

    std::vector<uint8_t> bits_;
    std::size_t num_bits_;
    std::size_t num_hashes_;
    std::size_t item_count_;
};

} // namespace sys
