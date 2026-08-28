#include <cstdint>
#include <cstddef>
#include <vector>
#include <span>
#include <bit>
#include <algorithm>
#include <limits>
#include <iostream>

class DynamicBitset {
public:
    static constexpr std::size_t npos = std::numeric_limits<std::size_t>::max();

    explicit DynamicBitset(std::size_t num_bits = 0)
        : num_bits_(num_bits),
          words_((num_bits + 63) / 64, 0ULL) {}

    [[nodiscard]] std::size_t size() const noexcept { return num_bits_; }
    [[nodiscard]] std::size_t word_count() const noexcept { return words_.size(); }
    [[nodiscard]] bool empty() const noexcept { return num_bits_ == 0; }

    void set(std::size_t i) {
        if (i < num_bits_) {
            words_[i >> 6] |= (1ULL << (i & 63));
        }
    }

    void reset(std::size_t i) {
        if (i < num_bits_) {
            words_[i >> 6] &= ~(1ULL << (i & 63));
        }
    }

    [[nodiscard]] bool test(std::size_t i) const noexcept {
        if (i >= num_bits_) return false;
        return (words_[i >> 6] & (1ULL << (i & 63))) != 0;
    }

    void reset_all() noexcept {
        std::fill(words_.begin(), words_.end(), 0ULL);
    }

    void set_all() noexcept {
        if (words_.empty()) return;
        std::fill(words_.begin(), words_.end(), ~0ULL);
        trim_tail();
    }

    /* Підрахунок потужності множини через std::popcount (C++20) */
    [[nodiscard]] std::size_t count() const noexcept {
        std::size_t total = 0;
        for (std::uint64_t w : words_) {
            total += static_cast<std::size_t>(std::popcount(w));
        }
        return total;
    }

    /* Пошук першого елемента через std::countr_zero (C++20) */
    [[nodiscard]] std::size_t find_first() const noexcept {
        for (std::size_t w = 0; w < words_.size(); ++w) {
            if (words_[w] != 0) {
                std::size_t pos = (w << 6) + static_cast<std::size_t>(std::countr_zero(words_[w]));
                return (pos < num_bits_) ? pos : npos;
            }
        }
        return npos;
    }

    /* Пошук наступного встановленого біта */
    [[nodiscard]] std::size_t find_next(std::size_t curr) const noexcept {
        size_t next_idx = curr + 1;
        if (next_idx >= num_bits_) return npos;

        std::size_t w = next_idx >> 6;
        std::size_t offset = next_idx & 63;

        std::uint64_t val = words_[w] & (~0ULL << offset);
        if (val != 0) {
            std::size_t pos = (w << 6) + static_cast<std::size_t>(std::countr_zero(val));
            return (pos < num_bits_) ? pos : npos;
        }

        for (++w; w < words_.size(); ++w) {
            if (words_[w] != 0) {
                std::size_t pos = (w << 6) + static_cast<std::size_t>(std::countr_zero(words_[w]));
                return (pos < num_bits_) ? pos : npos;
            }
        }
        return npos;
    }

    /* Побітові оператори над множинами */
    DynamicBitset& operator&=(const DynamicBitset& other) noexcept {
        std::size_t n = std::min(words_.size(), other.words_.size());
        for (std::size_t i = 0; i < n; ++i) {
            words_[i] &= other.words_[i];
        }
        return *this;
    }

    DynamicBitset& operator|=(const DynamicBitset& other) noexcept {
        std::size_t n = std::min(words_.size(), other.words_.size());
        for (std::size_t i = 0; i < n; ++i) {
            words_[i] |= other.words_[i];
        }
        trim_tail();
        return *this;
    }

    DynamicBitset& operator^=(const DynamicBitset& other) noexcept {
        std::size_t n = std::min(words_.size(), other.words_.size());
        for (std::size_t i = 0; i < n; ++i) {
            words_[i] ^= other.words_[i];
        }
        trim_tail();
        return *this;
    }

    DynamicBitset operator~() const {
        DynamicBitset res = *this;
        for (auto& w : res.words_) {
            w = ~w;
        }
        res.trim_tail();
        return res;
    }

    [[nodiscard]] std::span<const std::uint64_t> words() const noexcept {
        return words_;
    }

private:
    void trim_tail() noexcept {
        if (!words_.empty()) {
            std::size_t rem = num_bits_ & 63;
            if (rem != 0) {
                words_.back() &= ((1ULL << rem) - 1ULL);
            }
        }
    }

    std::size_t num_bits_{0};
    std::vector<std::uint64_t> words_{};
};
