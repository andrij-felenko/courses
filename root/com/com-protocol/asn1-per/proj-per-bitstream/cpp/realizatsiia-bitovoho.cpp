#include <iostream>
#include <vector>
#include <span>
#include <cstdint>
#include <expected>
#include <format>
#include <string_view>
#include <algorithm>

enum class BitError {
    BufferOverflow,
    UnexpectedEndOfStream,
    InvalidRange,
    ValueOutOfRange
};

class BitWriter {
public:
    explicit BitWriter(std::span<uint8_t> buffer) : buffer_(buffer), bit_pos_(0) {
        std::fill(buffer_.begin(), buffer_.end(), uint8_t{0});
    }

    [[nodiscard]] std::expected<void, BitError> put_bits(uint32_t value, uint8_t num_bits) {
        if (num_bits == 0) return {};
        if (num_bits > 32) return std::unexpected(BitError::InvalidRange);
        if ((bit_pos_ + num_bits) > (buffer_.size() * 8)) {
            return std::unexpected(BitError::BufferOverflow);
        }

        if (num_bits < 32) {
            value &= (1U << num_bits) - 1U;
        }

        int remaining = num_bits;
        while (remaining > 0) {
            size_t byte_idx = bit_pos_ / 8;
            uint8_t bit_in_byte = bit_pos_ % 8;
            uint8_t bits_free_in_byte = 8 - bit_in_byte;

            uint8_t bits_to_write = std::min<uint8_t>(remaining, bits_free_in_byte);
            uint8_t shift = remaining - bits_to_write;
            uint8_t chunk = static_cast<uint8_t>((value >> shift) & ((1U << bits_to_write) - 1U));

            buffer_[byte_idx] |= static_cast<uint8_t>(chunk << (bits_free_in_byte - bits_to_write));
            bit_pos_ += bits_to_write;
            remaining -= bits_to_write;
        }
        return {};
    }

    [[nodiscard]] std::expected<void, BitError> put_bit(bool bit) {
        return put_bits(bit ? 1U : 0U, 1);
    }

    [[nodiscard]] std::expected<void, BitError> put_constrained_int(int64_t val, int64_t lb, int64_t ub) {
        if (val < lb || val > ub) return std::unexpected(BitError::ValueOutOfRange);
        uint64_t range = static_cast<uint64_t>(ub - lb + 1);
        if (range == 1) return {};

        uint8_t bits = 0;
        uint64_t temp = range - 1;
        while (temp > 0) {
            bits++;
            temp >>= 1;
        }

        uint64_t offset = static_cast<uint64_t>(val - lb);
        if (bits <= 32) {
            return put_bits(static_cast<uint32_t>(offset), bits);
        } else {
            uint8_t high_bits = bits - 32;
            auto res = put_bits(static_cast<uint32_t>(offset >> 32), high_bits);
            if (!res) return res;
            return put_bits(static_cast<uint32_t>(offset & 0xFFFFFFFFU), 32);
        }
    }

    void align_to_byte() noexcept {
        size_t rem = bit_pos_ % 8;
        if (rem != 0) {
            bit_pos_ += (8 - rem);
        }
    }

    [[nodiscard]] size_t bit_position() const noexcept { return bit_pos_; }
    [[nodiscard]] size_t byte_length() const noexcept { return (bit_pos_ + 7) / 8; }

private:
    std::span<uint8_t> buffer_;
    size_t bit_pos_;
};

class BitReader {
public:
    explicit BitReader(std::span<const uint8_t> buffer)
        : buffer_(buffer), total_bits_(buffer.size() * 8), bit_pos_(0) {}

    [[nodiscard]] std::expected<uint32_t, BitError> get_bits(uint8_t num_bits) {
        if (num_bits == 0) return 0;
        if (num_bits > 32) return std::unexpected(BitError::InvalidRange);
        if (bit_pos_ + num_bits > total_bits_) {
            return std::unexpected(BitError::UnexpectedEndOfStream);
        }

        uint32_t result = 0;
        int remaining = num_bits;
        while (remaining > 0) {
            size_t byte_idx = bit_pos_ / 8;
            uint8_t bit_in_byte = bit_pos_ % 8;
            uint8_t bits_avail = 8 - bit_in_byte;

            uint8_t bits_to_read = std::min<uint8_t>(remaining, bits_avail);
            uint8_t shift = bits_avail - bits_to_read;
            uint8_t mask = (1U << bits_to_read) - 1U;
            uint8_t chunk = (buffer_[byte_idx] >> shift) & mask;

            result = (result << bits_to_read) | chunk;
            bit_pos_ += bits_to_read;
            remaining -= bits_to_read;
        }
        return result;
    }

    [[nodiscard]] std::expected<bool, BitError> get_bit() {
        auto res = get_bits(1);
        if (!res) return std::unexpected(res.error());
        return (*res != 0);
    }

    [[nodiscard]] std::expected<int64_t, BitError> get_constrained_int(int64_t lb, int64_t ub) {
        uint64_t range = static_cast<uint64_t>(ub - lb + 1);
        if (range == 1) return lb;

        uint8_t bits = 0;
        uint64_t temp = range - 1;
        while (temp > 0) {
            bits++;
            temp >>= 1;
        }

        if (bits <= 32) {
            auto raw = get_bits(bits);
            if (!raw) return std::unexpected(raw.error());
            int64_val = lb + static_cast<int64_t>(*raw);
            if (int64_val > ub) return std::unexpected(BitError::ValueOutOfRange);
            return int64_val;
        } else {
            uint8_t high_bits = bits - 32;
            auto raw_high = get_bits(high_bits);
            if (!raw_high) return std::unexpected(raw_high.error());
            auto raw_low = get_bits(32);
            if (!raw_low) return std::unexpected(raw_low.error());
            uint64_t raw = (static_cast<uint64_t>(*raw_high) << 32) | *raw_low;
            int64_t val = lb + static_cast<int64_t>(raw);
            if (val > ub) return std::unexpected(BitError::ValueOutOfRange);
            return val;
        }
    }

    void align_to_byte() noexcept {
        size_t rem = bit_pos_ % 8;
        if (rem != 0) {
            bit_pos_ += (8 - rem);
        }
    }

    [[nodiscard]] size_t bit_position() const noexcept { return bit_pos_; }

private:
    std::span<const uint8_t> buffer_;
    size_t total_bits_;
    size_t bit_pos_;
};
