#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <array>
#include <unordered_map>
#include <chrono>
#include <random>
#include <algorithm>
#include <cstdint>

namespace cache {

// 64-бітний алгоритм MurmurHash3
constexpr uint64_t murmurhash3_64(std::string_view data, uint32_t seed) noexcept {
    const size_t len = data.size();
    const size_t nblocks = len / 8;
    uint64_t h = seed ^ (len * 0xc6a4a7935bd1e995ULL);
    constexpr uint64_t m = 0xc6a4a7935bd1e995ULL;
    constexpr int r = 47;

    const auto* blocks = reinterpret_cast<const uint64_t*>(data.data());
    for (size_t i = 0; i < nblocks; ++i) {
        uint64_t k = blocks[i];
        k *= m;
        k ^= k >> r;
        k *= m;
        h ^= k;
        h *= m;
    }

    const auto* tail = reinterpret_cast<const uint8_t*>(data.data() + nblocks * 8);
    uint64_t k = 0;
    switch (len & 7) {
        case 7: k ^= static_cast<uint64_t>(tail[6]) << 48; [[fallthrough]];
        case 6: k ^= static_cast<uint64_t>(tail[5]) << 40; [[fallthrough]];
        case 5: k ^= static_cast<uint64_t>(tail[4]) << 32; [[fallthrough]];
        case 4: k ^= static_cast<uint64_t>(tail[3]) << 24; [[fallthrough]];
        case 3: k ^= static_cast<uint64_t>(tail[2]) << 16; [[fallthrough]];
        case 2: k ^= static_cast<uint64_t>(tail[1]) << 8;  [[fallthrough]];
        case 1: k ^= static_cast<uint64_t>(tail[0]);
                k *= m; k ^= k >> r; k *= m; h ^= k;
    }

    h ^= h >> r;
    h *= m;
    h ^= h >> r;
    return h;
}

// 1. Канонічний побудовник ключів
struct KeySpec {
    std::string_view service;
    std::string_view tenant;
    std::string_view entity;
    std::string_view id;
    std::string_view slot_tag{};
    uint32_t schema_version{1};
};

class CacheKeyBuilder {
public:
    static std::string build(const KeySpec& spec, std::string_view query_params = "") {
        std::string key;
        key.reserve(128);

        key += spec.service; key += ':';
        key += spec.tenant;  key += ':';
        key += spec.entity;  key += ':';
        key += spec.id;

        if (!spec.slot_tag.empty()) {
            key += ":{";
            key += spec.slot_tag;
            key += '}';
        }

        key += ":v";
        key += std::to_string(spec.schema_version);

        if (!query_params.empty()) {
            uint64_t h = murmurhash3_64(query_params, 0x9747b28c);
            key += ':';
            char hex_buf[17];
            snprintf(hex_buf, sizeof(hex_buf), "%016llx", static_cast<unsigned long long>(h));
            key += hex_buf;
        }

        return key;
    }
};

// 2. Потоковий детектор гарячих точок Count-Min Sketch
template <size_t Depth = 4, size_t Width = 2048>
class HeavyHitterDetector {
public:
    HeavyHitterDetector() {
        seeds_ = {0x1337beef, 0xdeadc0de, 0xcafebabe, 0x8badf00d};
        for (auto& row : table_) row.fill(0);
    }

    void record(std::string_view key) noexcept {
        for (size_t i = 0; i < Depth; ++i) {
            uint64_t h = murmurhash3_64(key, seeds_[i]);
            size_t col = h % Width;
            if (table_[i][col] < std::numeric_limits<uint32_t>::max()) {
                ++table_[i][col];
            }
        }
    }

    [[nodiscard]] uint32_t estimate(std::string_view key) const noexcept {
        uint32_t min_val = std::numeric_limits<uint32_t>::max();
        for (size_t i = 0; i < Depth; ++i) {
            uint64_t h = murmurhash3_64(key, seeds_[i]);
            size_t col = h % Width;
            min_val = std::min(min_val, table_[i][col]);
        }
        return min_val;
    }

    void decay() noexcept {
        for (auto& row : table_) {
            for (auto& cell : row) {
                cell /= 2;
            }
        }
    }

private:
    std::array<std::array<uint32_t, Width>, Depth> table_;
    std::array<uint32_t, Depth> seeds_;
};

// 3. Дворівневий адаптивний кеш-менеджер
class AdaptiveCacheManager {
public:
    struct L1Entry {
        std::string value;
        std::chrono::steady_clock::time_point expires_at;
    };

    AdaptiveCacheManager(uint32_t hot_threshold = 50, size_t salt_factor = 4)
        : hot_threshold_(hot_threshold), salt_factor_(salt_factor), rng_(std::random_device{}()) {}

    std::string get(const std::string& base_key) {
        auto now = std::chrono::steady_clock::now();

        // Перевірка L1 In-Process
        auto it = l1_cache_.find(base_key);
        if (it != l1_cache_.end() && it->second.expires_at > now) {
            return it->second.value;
        }

        // Фіксація звернення в CMS
        detector_.record(base_key);
        uint32_t freq = detector_.estimate(base_key);

        std::string fetch_key = base_key;
        if (freq >= hot_threshold_) {
            std::uniform_int_distribution<size_t> dist(0, salt_factor_ - 1);
            size_t salt = dist(rng_);
            fetch_key = base_key + "#" + std::to_string(salt);

            // Читаємо розщеплений ключ з L2 і кладемо в L1 на 3 секунди
            std::string val = mock_l2_get(fetch_key);
            l1_cache_[base_key] = L1Entry{val, now + std::chrono::seconds(3)};
            return val;
        }

        return mock_l2_get(fetch_key);
    }

    static void print_cluster_stats() {
        std::cout << "\nСтатистика звернень до 16 шардів L2-кластера:\n";
        for (size_t s = 0; s < shard_hits_.size(); ++s) {
            if (shard_hits_[s] > 0) {
                std::cout << "  Шард " << s << ": " << shard_hits_[s] << " запитів\n";
            }
        }
    }

    [[nodiscard]] uint32_t get_frequency(std::string_view key) const noexcept {
        return detector_.estimate(key);
    }

private:
    std::string mock_l2_get(std::string_view key) {
        uint64_t h = murmurhash3_64(key, 0x55aa55aa);
        size_t shard = h % shard_hits_.size();
        ++shard_hits_[shard];
        return "DataFor(" + std::string(key) + ")";
    }

    uint32_t hot_threshold_;
    size_t salt_factor_;
    HeavyHitterDetector<4, 2048> detector_;
    std::unordered_map<std::string, L1Entry> l1_cache_;
    std::mt19937 rng_;
    inline static std::array<size_t, 16> shard_hits_{};
};

} // namespace cache

int main() {
    cache::KeySpec spec{
        .service = "catalog",
        .tenant = "client_ua",
        .entity = "product",
        .id = "9901",
        .slot_tag = "prod_9901",
        .schema_version = 2
    };

    std::string canonical_key = cache::CacheKeyBuilder::build(spec, "category=electronics&sort=asc");
    std::cout << "Згенеровано канонічний ключ:\n  " << canonical_key << "\n\n";

    cache::AdaptiveCacheManager manager(50, 4);

    std::cout << "Симуляція 200 паралельних запитів...\n";
    for (int i = 0; i < 200; ++i) {
        manager.get(canonical_key);
    }

    cache::AdaptiveCacheManager::print_cluster_stats();
    std::cout << "Оцінена частота ключа в CMS: " << manager.get_frequency(canonical_key) << '\n';

    return 0;
}
