#include <cstdint>
#include <vector>
#include <span>
#include <array>
#include <memory>
#include <expected>
#include <string_view>
#include <algorithm>

namespace algorithms {

enum class FilterError {
    EmptyInput,
    AllocationFailure,
    PeelingFailedExceededAttempts
};

template <typename FingerprintType = uint8_t>
class XorFilter {
public:
    static constexpr double OverheadFactor = 1.23;
    static constexpr int MaxBuildAttempts = 64;

    XorFilter() noexcept = default;

    /* Фабричний метод побудови фільтра з послідовності ключів */
    [[nodiscard]] static std::expected<XorFilter, FilterError>
    build(std::span<const uint64_t> keys) {
        if (keys.empty()) {
            return std::unexpected(FilterError::EmptyInput);
        }

        const size_t count = keys.size();
        uint32_t block_len = static_cast<uint32_t>((OverheadFactor * static_cast<double>(count)) / 3.0) + 1;
        if (block_len < 32) block_len = 32;
        const uint32_t total_slots = 3 * block_len;

        std::vector<uint8_t> hcount(total_slots, 0);
        std::vector<uint64_t> hxor(total_slots, 0);
        std::vector<uint32_t> queue(total_slots, 0);

        struct PeelEntry {
            uint64_t key;
            uint32_t index;
        };
        std::vector<PeelEntry> stack;
        stack.reserve(count);

        uint64_t seed = 0x8543290134ULL;
        bool success = false;

        for (int attempt = 0; attempt < MaxBuildAttempts; ++attempt) {
            seed = hash64(seed + attempt, 0x9e3779b97f4a7c15ULL);
            std::fill(hcount.begin(), hcount.end(), 0);
            std::fill(hxor.begin(), hxor.end(), 0);
            stack.clear();

            for (uint64_t key : keys) {
                auto [h0, h1, h2] = get_positions(key, seed, block_len);
                hcount[h0]++; hxor[h0] ^= key;
                hcount[h1]++; hxor[h1] ^= key;
                hcount[h2]++; hxor[h2] ^= key;
            }

            uint32_t q_head = 0, q_tail = 0;
            for (uint32_t i = 0; i < total_slots; ++i) {
                if (hcount[i] == 1) {
                    queue[q_tail++] = i;
                }
            }

            while (q_head < q_tail) {
                uint32_t slot = queue[q_head++];
                if (hcount[slot] != 1) continue;

                uint64_t key = hxor[slot];
                stack.push_back({key, slot});

                auto [h0, h1, h2] = get_positions(key, seed, block_len);
                const std::array<uint32_t, 3> neighbors = {h0, h1, h2};

                for (uint32_t neighbor : neighbors) {
                    hcount[neighbor]--;
                    hxor[neighbor] ^= key;
                    if (hcount[neighbor] == 1) {
                        queue[q_tail++] = neighbor;
                    }
                }
            }

            if (stack.size() == count) {
                success = true;
                break;
            }
        }

        if (!success) {
            return std::unexpected(FilterError::PeelingFailedExceededAttempts);
        }

        /* Фаза зворотної підстановки */
        XorFilter filter;
        filter.seed_ = seed;
        filter.block_length_ = block_len;
        filter.fingerprints_.resize(total_slots, 0);

        for (auto it = stack.rbegin(); it != stack.rend(); ++it) {
            const uint64_t key = it->key;
            const uint32_t slot = it->index;
            const FingerprintType fp = compute_fingerprint(key, filter.seed_);

            auto [h0, h1, h2] = get_positions(key, filter.seed_, block_len);
            const std::array<uint32_t, 3> pos = {h0, h1, h2};

            FingerprintType other_xor = 0;
            for (uint32_t p : pos) {
                if (p != slot) {
                    other_xor ^= filter.fingerprints_[p];
                }
            }
            filter.fingerprints_[slot] = fp ^ other_xor;
        }

        return filter;
    }

    /* Швидка перевірка належності O(1) */
    [[nodiscard]] bool contains(uint64_t key) const noexcept {
        if (fingerprints_.empty()) return false;

        auto [h0, h1, h2] = get_positions(key, seed_, block_length_);
        const FingerprintType fp = compute_fingerprint(key, seed_);

        const FingerprintType combined = fingerprints_[h0] ^
                                         fingerprints_[h1] ^
                                         fingerprints_[h2];

        return (combined == fp);
    }

    [[nodiscard]] size_t size_in_bytes() const noexcept {
        return sizeof(*this) + fingerprints_.size() * sizeof(FingerprintType);
    }

    [[nodiscard]] uint32_t block_length() const noexcept { return block_length_; }
    [[nodiscard]] uint64_t seed() const noexcept { return seed_; }

private:
    uint64_t seed_{0};
    uint32_t block_length_{0};
    std::vector<FingerprintType> fingerprints_;

    static constexpr uint64_t hash64(uint64_t x, uint64_t seed) noexcept {
        x ^= seed;
        x ^= x >> 33;
        x *= 0xff51afd7ed558ccdULL;
        x ^= x >> 33;
        x *= 0xc4ceb9fe1a85ec53ULL;
        x ^= x >> 33;
        return x;
    }

    static constexpr uint32_t reduce(uint32_t hash, uint32_t n) noexcept {
        return static_cast<uint32_t>((static_cast<uint64_t>(hash) * static_cast<uint64_t>(n)) >> 32);
    }

    static std::array<uint32_t, 3> get_positions(uint64_t key, uint64_t seed, uint32_t block_len) noexcept {
        const uint64_t hash = hash64(key, seed);
        const uint32_t a = static_cast<uint32_t>(hash >> 32);
        const uint32_t b = static_cast<uint32_t>(hash);
        const uint32_t c = static_cast<uint32_t>(hash ^ (hash >> 16));

        return {
            reduce(a, block_len),
            block_len + reduce(b, block_len),
            2 * block_len + reduce(c, block_len)
        };
    }

    static FingerprintType compute_fingerprint(uint64_t key, uint64_t seed) noexcept {
        const uint64_t hash = hash64(key, ~seed);
        auto fp = static_cast<FingerprintType>(hash ^ (hash >> 32));
        return (fp == 0) ? 1 : fp;
    }
};

} // namespace algorithms
