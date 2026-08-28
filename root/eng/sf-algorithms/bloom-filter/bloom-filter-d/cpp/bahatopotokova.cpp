#include <atomic>
#include <vector>
#include <cstddef>
#include <memory_resource>

class concurrent_bloom_filter {
public:
    explicit concurrent_bloom_filter(std::size_t num_bits)
        : num_bits_(num_bits), bits_((num_bits + 7) / 8) {
        for (auto& b : bits_) b.store(0, std::memory_order_relaxed);
    }

    void set_bit_atomic(std::size_t bit_index) noexcept {
        std::size_t byte_idx = bit_index >> 3;
        std::uint8_t mask = static_cast<std::uint8_t>(1u << (bit_index & 7));
        bits_[byte_idx].fetch_or(mask, std::memory_order_relaxed);
    }

private:
    std::size_t num_bits_;
    std::vector<std::atomic<std::uint8_t>> bits_;
};
