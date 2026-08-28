#include <vector>
#include <cstdint>
#include <cstddef>
#include <span>

class DynamicBitset {
public:
    explicit DynamicBitset(std::size_t num_bits)
        : size_(num_bits), words_((num_bits + 63) / 64, 0ULL) {}

    void set(std::size_t i) noexcept {
        words_[i >> 6] |= (1ULL << (i & 63));
    }

    void clear(std::size_t i) noexcept {
        words_[i >> 6] &= ~(1ULL << (i & 63));
    }

    [[nodiscard]] bool test(std::size_t i) const noexcept {
        return (words_[i >> 6] & (1ULL << (i & 63))) != 0;
    }

    [[nodiscard]] std::size_t size() const noexcept { return size_; }
    [[nodiscard]] std::span<const std::uint64_t> raw_words() const noexcept { return words_; }

private:
    std::size_t size_;
    std::vector<std::uint64_t> words_;
};
