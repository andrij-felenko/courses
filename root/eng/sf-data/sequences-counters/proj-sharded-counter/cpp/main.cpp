#include <atomic>
#include <vector>
#include <cstdint>
#include <new>
#include <numeric>

class ShardedCounter {
public:
    // Апаратне вирівнювання на розмір лінії кешу процесора
    static constexpr size_t CacheLineSize = 64;

    struct alignas(CacheLineSize) Shard {
        std::atomic<uint64_t> value{0};
    };

    explicit ShardedCounter(size_t num_shards = 16) {
        size_t power = 1;
        while (power < num_shards) {
            power <<= 1;
        }
        shards_.resize(power);
        mask_ = power - 1;
    }

    void Add(size_t thread_id, uint64_t delta = 1) noexcept {
        const size_t slot = thread_id & mask_;
        shards_[slot].value.fetch_add(delta, std::memory_order_relaxed);
    }

    [[nodiscard]] uint64_t Get() const noexcept {
        uint64_t total = 0;
        for (const auto& shard : shards_) {
            total += shard.value.load(std::memory_order_relaxed);
        }
        return total;
    }

private:
    std::vector<Shard> shards_;
    size_t mask_;
};
