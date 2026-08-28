#include <iostream>
#include <vector>
#include <string_view>
#include <span>
#include <cmath>
#include <numeric>
#include <algorithm>
#include <random>
#include <memory>
#include <queue>
#include <unordered_map>
#include <string>

class CountMinSketch {
public:
    struct HashParam {
        uint64_t a{0};
        uint64_t b{0};
    };

    CountMinSketch(double epsilon, double delta, uint32_t seed = 42)
        : width_(static_cast<uint32_t>(std::ceil(std::numbers::e / epsilon))),
          depth_(static_cast<uint32_t>(std::ceil(std::log(1.0 / delta)))),
          table_(static_cast<size_t>(depth_) * width_, 0),
          total_count_(0) {
        
        std::mt19937_64 rng(seed);
        std::uniform_int_distribution<uint64_t> dist;
        
        params_.reserve(depth_);
        for (uint32_t i = 0; i < depth_; ++i) {
            params_.push_back({dist(rng) | 1ULL, dist(rng)});
        }
    }

    void update(std::string_view key, uint32_t count = 1) noexcept {
        if (count == 0) return;
        for (uint32_t r = 0; r < depth_; ++r) {
            uint32_t col = get_column(r, key);
            table_[static_cast<size_t>(r) * width_ + col] += count;
        }
        total_count_ += count;
    }

    void update_conservative(std::string_view key, uint32_t count = 1) {
        if (count == 0) return;
        
        std::vector<uint32_t> cols(depth_);
        uint32_t min_val = std::numeric_limits<uint32_t>::max();
        
        for (uint32_t r = 0; r < depth_; ++r) {
            cols[r] = get_column(r, key);
            min_val = std::min(min_val, table_[static_cast<size_t>(r) * width_ + cols[r]]);
        }
        
        uint32_t new_min = min_val + count;
        for (uint32_t r = 0; r < depth_; ++r) {
            size_t idx = static_cast<size_t>(r) * width_ + cols[r];
            table_[idx] = std::max(table_[idx], new_min);
        }
        total_count_ += count;
    }

    [[nodiscard]] uint32_t estimate(std::string_view key) const noexcept {
        uint32_t min_val = std::numeric_limits<uint32_t>::max();
        for (uint32_t r = 0; r < depth_; ++r) {
            uint32_t col = get_column(r, key);
            min_val = std::min(min_val, table_[static_cast<size_t>(r) * width_ + col]);
        }
        return min_val;
    }

    [[nodiscard]] bool merge(const CountMinSketch& other) noexcept {
        if (depth_ != other.depth_ || width_ != other.width_) return false;
        
        for (size_t i = 0; i < table_.size(); ++i) {
            table_[i] += other.table_[i];
        }
        total_count_ += other.total_count_;
        return true;
    }

    [[nodiscard]] uint32_t width() const noexcept { return width_; }
    [[nodiscard]] uint32_t depth() const noexcept { return depth_; }
    [[nodiscard]] uint64_t total_count() const noexcept { return total_count_; }

private:
    [[nodiscard]] static uint64_t hash_bytes(std::string_view key, uint64_t seed) noexcept {
        uint64_t h = seed ^ (key.size() * 0xc6a4a7935bd1e995ULL);
        const auto* data = reinterpret_cast<const uint8_t*>(key.data());
        size_t len = key.size();
        
        while (len >= 8) {
            uint64_t k;
            std::memcpy(&k, data, sizeof(uint64_t));
            k *= 0xc6a4a7935bd1e995ULL;
            k ^= k >> 47;
            k *= 0xc6a4a7935bd1e995ULL;
            h ^= k;
            h *= 0xc6a4a7935bd1e995ULL;
            data += 8;
            len -= 8;
        }
        
        if (len > 0) {
            uint64_t tail = 0;
            std::memcpy(&tail, data, len);
            h ^= tail;
            h *= 0xc6a4a7935bd1e995ULL;
        }
        
        h ^= h >> 47;
        h *= 0xc6a4a7935bd1e995ULL;
        h ^= h >> 47;
        return h;
    }

    [[nodiscard]] uint32_t get_column(uint32_t row, std::string_view key) const noexcept {
        uint64_t raw = hash_bytes(key, params_[row].b);
        return static_cast<uint32_t>((raw ^ params_[row].a) % width_);
    }

    uint32_t width_;
    uint32_t depth_;
    std::vector<uint32_t> table_;
    std::vector<HashParam> params_;
    uint64_t total_count_;
};
