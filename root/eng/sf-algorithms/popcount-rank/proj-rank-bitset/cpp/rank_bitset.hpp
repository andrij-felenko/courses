/* rank_bitset.hpp — Ідіоматична реалізація бітового вектора мовою C++20 */
#pragma once

#include <bit>
#include <cstdint>
#include <cstddef>
#include <vector>
#include <span>
#include <optional>
#include <stdexcept>
#include <memory>
#include <algorithm>
#include <new>

namespace ds {

struct alignas(16) Rank9Block {
    uint64_t abs_rank{0};  // Абсолютна сума одиниць до початку суперблока
    uint64_t offsets{0};   // 7 упакованих 9-бітних лічильників
};

class SuccinctBitVector {
public:
    explicit SuccinctBitVector(size_t num_bits)
        : num_bits_(num_bits),
          num_words_((num_bits + 63) / 64),
          num_blocks_((num_bits + 511) / 512),
          total_ones_(0),
          index_built_(false) {
        if (num_bits == 0) {
            throw std::invalid_argument("Розмір бітового вектора має перевищувати 0");
        }
        data_.resize(num_blocks_ * 8, 0ULL);
        index_.resize(num_blocks_);
    }

    void set(size_t bit_idx) {
        if (bit_idx >= num_bits_) {
            throw std::out_of_range("Індекс біта виходить за межі вектора");
        }
        data_[bit_idx / 64] |= (1ULL << (bit_idx % 64));
        index_built_ = false;
    }

    [[nodiscard]] bool test(size_t bit_idx) const {
        if (bit_idx >= num_bits_) {
            throw std::out_of_range("Індекс біта виходить за межі вектора");
        }
        return (data_[bit_idx / 64] & (1ULL << (bit_idx % 64))) != 0;
    }

    void build_index() noexcept {
        uint64_t running_total = 0;

        for (size_t b = 0; b < num_blocks_; ++b) {
            index_[b].abs_rank = running_total;
            uint64_t packed_offsets = 0;
            uint64_t block_sum = 0;

            for (int w = 0; w < 7; ++w) {
                const uint64_t word_val = data_[b * 8 + static_cast<size_t>(w)];
                block_sum += static_cast<uint64_t>(std::popcount(word_val));
                packed_offsets |= (block_sum & 0x1FFULL) << (w * 9);
            }

            index_[b].offsets = packed_offsets;

            const uint64_t last_word = data_[b * 8 + 7];
            block_sum += static_cast<uint64_t>(std::popcount(last_word));
            running_total += block_sum;
        }

        total_ones_ = running_total;
        index_built_ = true;
    }

    [[nodiscard]] size_t rank1(size_t bit_idx) const noexcept {
        if (bit_idx >= num_bits_) {
            bit_idx = num_bits_ - 1;
        }

        const size_t block_idx = bit_idx / 512;
        const size_t word_in_block = (bit_idx % 512) / 64;
        const size_t bit_in_word = bit_idx % 64;

        uint64_t rank = index_[block_idx].abs_rank;

        if (word_in_block > 0) {
            const int shift = static_cast<int>(word_in_block - 1) * 9;
            rank += (index_[block_idx].offsets >> shift) & 0x1FFULL;
        }

        const uint64_t word = data_[block_idx * 8 + word_in_block];
        const uint64_t mask = (bit_in_word == 63) ? ~0ULL : ((1ULL << (bit_in_word + 1)) - 1ULL);
        rank += static_cast<uint64_t>(std::popcount(word & mask));

        return static_cast<size_t>(rank);
    }

    [[nodiscard]] size_t rank0(size_t bit_idx) const noexcept {
        if (bit_idx >= num_bits_) bit_idx = num_bits_ - 1;
        return (bit_idx + 1) - rank1(bit_idx);
    }

    [[nodiscard]] std::optional<size_t> select1(size_t k) const noexcept {
        if (k == 0 || k > total_ones_ || !index_built_) {
            return std::nullopt;
        }

        // Двійковий пошук по масиву abs_rank
        auto it = std::upper_bound(index_.begin(), index_.end(), k - 1,
            [](uint64_t val, const Rank9Block& block) {
                return val < block.abs_rank;
            });
        
        const size_t block_idx = static_cast<size_t>(std::distance(index_.begin(), it) - 1);
        const uint64_t k_rem = k - index_[block_idx].abs_rank;

        size_t target_word = 0;
        uint64_t prev_offset = 0;

        for (int w = 1; w < 8; ++w) {
            uint64_t cur_offset = 0;
            if (w < 7) {
                cur_offset = (index_[block_idx].offsets >> ((w - 1) * 9)) & 0x1FFULL;
            } else {
                const uint64_t w6 = data_[block_idx * 8 + 6];
                cur_offset = ((index_[block_idx].offsets >> (5 * 9)) & 0x1FFULL) + 
                             static_cast<uint64_t>(std::popcount(w6));
            }

            if (cur_offset >= k_rem) {
                target_word = static_cast<size_t>(w - 1);
                break;
            }
            prev_offset = cur_offset;
            if (w == 7) target_word = 7;
        }

        const uint64_t in_word_k = k_rem - prev_offset;
        const uint64_t word_val = data_[block_idx * 8 + target_word];

        size_t low = 0, high = 63, result_bit = 63;
        while (low <= high) {
            size_t mid = low + (high - low) / 2;
            const uint64_t mask = (mid == 63) ? ~0ULL : ((1ULL << (mid + 1)) - 1ULL);
            if (static_cast<uint64_t>(std::popcount(word_val & mask)) >= in_word_k) {
                result_bit = mid;
                if (mid == 0) break;
                high = mid - 1;
            } else {
                low = mid + 1;
            }
        }

        return block_idx * 512 + target_word * 64 + result_bit;
    }

    [[nodiscard]] size_t size() const noexcept { return num_bits_; }
    [[nodiscard]] size_t total_ones() const noexcept { return total_ones_; }
    [[nodiscard]] bool is_indexed() const noexcept { return index_built_; }
    [[nodiscard]] std::span<const uint64_t> raw_data() const noexcept {
        return std::span<const uint64_t>(data_.data(), num_words_);
    }

private:
    size_t num_bits_;
    size_t num_words_;
    size_t num_blocks_;
    uint64_t total_ones_;
    bool index_built_;
    std::vector<uint64_t> data_;
    std::vector<Rank9Block> index_;
};

// Векторизований валовий підрахунок одиниць через компресор Harley-Seal (CSA 3:2)
[[nodiscard]] inline uint64_t count_ones_csa(std::span<const uint64_t> data) noexcept {
    uint64_t total = 0;
    size_t i = 0;
    const size_t n = data.size();

    while (i + 2 < n) {
        const uint64_t a = data[i];
        const uint64_t b = data[i + 1];
        const uint64_t c = data[i + 2];

        const uint64_t sum = a ^ b ^ c;
        const uint64_t carry = (a & b) | (b & c) | (c & a);

        total += static_cast<uint64_t>(std::popcount(sum));
        total += 2ULL * static_cast<uint64_t>(std::popcount(carry));
        i += 3;
    }

    while (i < n) {
        total += static_cast<uint64_t>(std::popcount(data[i]));
        ++i;
    }
    return total;
}

} // namespace ds
