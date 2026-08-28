#include <array>
#include <cstdint>
#include <optional>
#include <random>
#include <utility>
#include <vector>

template <typename Key = uint64_t, typename Value = uint64_t>
class CuckooMap {
public:
    static constexpr size_t StashCapacity = 4;
    static constexpr size_t MaxDisplacementsFactor = 2;

    struct Entry {
        Key key{};
        Value value{};
        bool occupied{false};
    };

    explicit CuckooMap(size_t initial_capacity = 16)
        : capacity_(std::max<size_t>(initial_capacity, 8)), size_(0) {
        std::random_device rd;
        seed1_ = (static_cast<uint64_t>(rd()) << 32) | rd();
        seed2_ = (static_cast<uint64_t>(rd()) << 32) | rd();
        t1_.resize(capacity_);
        t2_.resize(capacity_);
    }

    [[nodiscard]] size_t size() const noexcept { return size_; }
    [[nodiscard]] size_t capacity() const noexcept { return capacity_ * 2; }
    [[nodiscard]] bool empty() const noexcept { return size_ == 0; }

private:
    std::vector<Entry> t1_;
    std::vector<Entry> t2_;
    std::array<Entry, StashCapacity> stash_{};
    size_t capacity_;
    size_t size_;
    uint64_t seed1_;
    uint64_t seed2_;

    static uint64_t splitmix(uint64_t x, uint64_t seed) noexcept {
        uint64_t z = (x + seed + 0x9E3779B97F4A7C15ULL);
        z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9ULL;
        z = (z ^ (z >> 27)) * 0x94D049BB133111EBULL;
        return z ^ (z >> 31);
    }

    [[nodiscard]] size_t index1(const Key &k) const noexcept {
        return static_cast<size_t>(splitmix(static_cast<uint64_t>(k), seed1_) % capacity_);
    }

    [[nodiscard]] size_t index2(const Key &k) const noexcept {
        return static_cast<size_t>(splitmix(static_cast<uint64_t>(k), seed2_) % capacity_);
    }
};
