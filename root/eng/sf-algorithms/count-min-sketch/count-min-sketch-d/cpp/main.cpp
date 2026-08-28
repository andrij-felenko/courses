#include <vector>
#include <string_view>
#include <limits>
#include <cstdint>
#include <algorithm>

class CountMinSketchMini {
public:
    CountMinSketchMini(uint32_t width, uint32_t depth)
        : width_(width), depth_(depth), table_(static_cast<size_t>(width) * depth, 0) {
        seeds_.reserve(depth);
        for (uint32_t i = 0; i < depth; ++i) {
            seeds_.push_back(0x9e3779b97f4a7c15ULL * (i + 1));
        }
    }

    void add(std::string_view key, uint32_t count = 1) noexcept {
        for (uint32_t r = 0; r < depth_; ++r) {
            uint32_t col = hash_key(key, seeds_[r]) % width_;
            table_[static_cast<size_t>(r) * width_ + col] += count;
        }
    }

    [[nodiscard]] uint32_t query(std::string_view key) const noexcept {
        uint32_t res = std::numeric_limits<uint32_t>::max();
        for (uint32_t r = 0; r < depth_; ++r) {
            uint32_t col = hash_key(key, seeds_[r]) % width_;
            res = std::min(res, table_[static_cast<size_t>(r) * width_ + col]);
        }
        return res;
    }

private:
    static uint32_t hash_key(std::string_view key, uint64_t seed) noexcept {
        uint32_t h = static_cast<uint32_t>(seed) ^ static_cast<uint32_t>(key.size());
        for (char c : key) {
            h ^= static_cast<uint8_t>(c);
            h *= 0x5bd1e995;
            h ^= h >> 15;
        }
        return h;
    }

    uint32_t width_;
    uint32_t depth_;
    std::vector<uint32_t> table_;
    std::vector<uint64_t> seeds_;
};
