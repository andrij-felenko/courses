#include <iostream>
#include <vector>
#include <array>
#include <string_view>
#include <cstdint>
#include <random>
#include <optional>

template <typename KeyType = std::string_view, size_t BucketSize = 4, size_t MaxKicks = 500>
class CuckooFilter {
public:
    using Fingerprint = uint8_t;
    static constexpr Fingerprint EmptySlot = 0;

    explicit CuckooFilter(size_t target_capacity) {
        size_t min_buckets = (target_capacity + BucketSize - 1) / BucketSize;
        num_buckets_ = 16;
        while (num_buckets_ < min_buckets) {
            num_buckets_ <<= 1;
        }
        bucket_mask_ = num_buckets_ - 1;
        buckets_.resize(num_buckets_);
        for (auto &b : buckets_) {
            b.fill(EmptySlot);
        }
    }

    [[nodiscard]] bool contains(KeyType key) const noexcept {
        const auto [fp, i1, i2] = compute_indices(key);
        return bucket_contains(i1, fp) || bucket_contains(i2, fp);
    }

    [[nodiscard]] bool insert(KeyType key) {
        const auto [fp, i1, i2] = compute_indices(key);

        if (insert_into_bucket(i1, fp) || insert_into_bucket(i2, fp)) {
            ++count_;
            return true;
        }

        size_t curr_i = (rng_() & 1) ? i1 : i2;
        Fingerprint curr_fp = fp;

        for (size_t kick = 0; kick < MaxKicks; ++kick) {
            size_t slot_idx = rng_() % BucketSize;
            std::swap(curr_fp, buckets_[curr_i][slot_idx]);

            curr_i = (curr_i ^ hash_fingerprint(curr_fp)) & bucket_mask_;

            if (insert_into_bucket(curr_i, curr_fp)) {
                ++count_;
                return true;
            }
        }

        return false;
    }

    [[nodiscard]] bool erase(KeyType key) noexcept {
        const auto [fp, i1, i2] = compute_indices(key);

        if (remove_from_bucket(i1, fp) || remove_from_bucket(i2, fp)) {
            --count_;
            return true;
        }
        return false;
    }

    [[nodiscard]] double load_factor() const noexcept {
        return static_cast<double>(count_) / static_cast<double>(num_buckets_ * BucketSize);
    }

    [[nodiscard]] size_t size() const noexcept { return count_; }
    [[nodiscard]] size_t capacity() const noexcept { return num_buckets_ * BucketSize; }

private:
    using Bucket = std::array<Fingerprint, BucketSize>;

    std::vector<Bucket> buckets_;
    size_t num_buckets_{0};
    size_t bucket_mask_{0};
    size_t count_{0};
    mutable std::mt19937 rng_{1337};

    static constexpr uint64_t fnv1a(std::string_view s) noexcept {
        uint64_t hash = 14695981039346656037ULL;
        for (char c : s) {
            hash ^= static_cast<uint8_t>(c);
            hash *= 1099511628211ULL;
        }
        return hash;
    }

    static constexpr size_t hash_fingerprint(Fingerprint fp) noexcept {
        return static_cast<size_t>(fp * 0x9E3779B97F4A7C15ULL);
    }

    struct KeyMeta {
        Fingerprint fp;
        size_t i1;
        size_t i2;
    };

    [[nodiscard]] KeyMeta compute_indices(KeyType key) const noexcept {
        uint64_t h = fnv1a(key);
        Fingerprint fp = static_cast<Fingerprint>(h & 0xFF);
        if (fp == EmptySlot) fp = 1;

        size_t i1 = (h >> 8) & bucket_mask_;
        size_t i2 = (i1 ^ hash_fingerprint(fp)) & bucket_mask_;
        return {fp, i1, i2};
    }

    [[nodiscard]] bool bucket_contains(size_t idx, Fingerprint fp) const noexcept {
        for (const auto &slot : buckets_[idx]) {
            if (slot == fp) return true;
        }
        return false;
    }

    [[nodiscard]] bool insert_into_bucket(size_t idx, Fingerprint fp) noexcept {
        for (auto &slot : buckets_[idx]) {
            if (slot == EmptySlot) {
                slot = fp;
                return true;
            }
        }
        return false;
    }

    [[nodiscard]] bool remove_from_bucket(size_t idx, Fingerprint fp) noexcept {
        for (auto &slot : buckets_[idx]) {
            if (slot == fp) {
                slot = EmptySlot;
                return true;
            }
        }
        return false;
    }
};
