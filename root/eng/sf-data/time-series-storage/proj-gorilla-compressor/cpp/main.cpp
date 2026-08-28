#include <cstdint>
#include <cstddef>
#include <vector>
#include <span>
#include <bit>
#include <bitset>
#include <cstring>
#include <optional>
#include <stdexcept>

class BitWriter {
public:
    explicit BitWriter(std::vector<uint8_t>& target)
        : out_buffer_(target), byte_pos_(0), bit_pos_(8) {
        if (out_buffer_.empty()) {
            out_buffer_.push_back(0);
        }
    }

    void write_bits(uint64_t value, int num_bits) {
        for (int i = num_bits - 1; i >= 0; --i) {
            uint8_t bit = static_cast<uint8_t>((value >> i) & 1ULL);
            bit_pos_--;
            out_buffer_[byte_pos_] |= static_cast<uint8_t>(bit << bit_pos_);
            if (bit_pos_ == 0) {
                bit_pos_ = 8;
                byte_pos_++;
                out_buffer_.push_back(0);
            }
        }
    }

    [[nodiscard]] size_t finalize() {
        if (bit_pos_ == 8 && !out_buffer_.empty() && byte_pos_ < out_buffer_.size()) {
            out_buffer_.pop_back(); // Прибираємо невикористаний нульовий байт
        }
        return out_buffer_.size();
    }

private:
    std::vector<uint8_t>& out_buffer_;
    size_t byte_pos_;
    uint8_t bit_pos_;
};

struct DataPoint {
    uint64_t timestamp;
    double value;
};

class GorillaCompressor {
public:
    explicit GorillaCompressor(std::vector<uint8_t>& output_sink)
        : writer_(output_sink) {}

    void append(const DataPoint& point) {
        encode_timestamp(point.timestamp);
        encode_value(point.value);
        count_++;
    }

    size_t close() {
        return writer_.finalize();
    }

    [[nodiscard]] size_t sample_count() const noexcept { return count_; }

private:
    BitWriter writer_;
    uint64_t prev_time_{0};
    uint64_t prev_delta_{0};
    uint64_t prev_val_bits_{0};
    int prev_leading_{64};
    int prev_trailing_{64};
    size_t count_{0};

    void encode_timestamp(uint64_t t) {
        if (count_ == 0) {
            writer_.write_bits(t, 64);
            prev_time_ = t;
            return;
        }
        if (count_ == 1) {
            uint64_t delta = t - prev_time_;
            writer_.write_bits(delta, 14);
            prev_delta_ = delta;
            prev_time_ = t;
            return;
        }

        uint64_t delta = t - prev_time_;
        int64_t dod = static_cast<int64_t>(delta) - static_cast<int64_t>(prev_delta_);

        if (dod == 0) {
            writer_.write_bits(0, 1);
        } else if (dod >= -63 && dod <= 64) {
            writer_.write_bits(2, 2); // Префікс '10'
            writer_.write_bits(static_cast<uint64_t>(dod & 0x7F), 7);
        } else if (dod >= -255 && dod <= 256) {
            writer_.write_bits(6, 3); // Префікс '110'
            writer_.write_bits(static_cast<uint64_t>(dod & 0x1FF), 9);
        } else if (dod >= -2047 && dod <= 2048) {
            writer_.write_bits(14, 4); // Префікс '1110'
            writer_.write_bits(static_cast<uint64_t>(dod & 0xFFF), 12);
        } else {
            writer_.write_bits(15, 4); // Префікс '1111'
            writer_.write_bits(static_cast<uint32_t>(dod), 32);
        }

        prev_delta_ = delta;
        prev_time_ = t;
    }

    void encode_value(double val) {
        uint64_t val_bits = std::bit_cast<uint64_t>(val);

        if (count_ == 0) {
            writer_.write_bits(val_bits, 64);
            prev_val_bits_ = val_bits;
            return;
        }

        uint64_t xor_val = val_bits ^ prev_val_bits_;
        if (xor_val == 0) {
            writer_.write_bits(0, 1);
        } else {
            writer_.write_bits(1, 1);

            int leading = std::countl_zero(xor_val);
            int trailing = std::countr_zero(xor_val);
            if (leading >= 32) leading = 31;

            if (prev_leading_ != 64 &&
                leading >= prev_leading_ &&
                trailing >= prev_trailing_) {
                writer_.write_bits(0, 1);
                int meaningful_len = 64 - prev_leading_ - prev_trailing_;
                uint64_t meaningful_bits = (xor_val >> prev_trailing_);
                writer_.write_bits(meaningful_bits, meaningful_len);
            } else {
                writer_.write_bits(1, 1);
                writer_.write_bits(static_cast<uint64_t>(leading), 5);
                int meaningful_len = 64 - leading - trailing;
                writer_.write_bits(static_cast<uint64_t>(meaningful_len), 6);
                uint64_t meaningful_bits = (xor_val >> trailing);
                writer_.write_bits(meaningful_bits, meaningful_len);

                prev_leading_ = leading;
                prev_trailing_ = trailing;
            }
        }

        prev_val_bits_ = val_bits;
    }
};
