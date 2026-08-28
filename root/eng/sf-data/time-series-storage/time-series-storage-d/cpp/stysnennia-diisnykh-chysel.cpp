#include <cstdint>
#include <bit>
#include <cstring>
#include <tuple>

class FloatXorEncoder {
public:
    struct EncodedFloat {
        uint64_t bits{0};
        int bit_length{0};
        bool is_new_window{false};
        int leading_zeros{0};
        int meaningful_length{0};
    };

    EncodedFloat encode(double value) noexcept {
        uint64_t val_bits = std::bit_cast<uint64_t>(value);

        if (is_first_) {
            prev_val_bits_ = val_bits;
            is_first_ = false;
            return {val_bits, 64, false, 0, 64};
        }

        uint64_t xor_val = val_bits ^ prev_val_bits_;
        prev_val_bits_ = val_bits;

        if (xor_val == 0) {
            return {0ULL, 1, false, 0, 0}; // 1 біт '0'
        }

        int leading = std::countl_zero(xor_val);
        int trailing = std::countr_zero(xor_val);
        if (leading >= 32) leading = 31;

        if (prev_leading_ != 64 &&
            leading >= prev_leading_ &&
            trailing >= prev_trailing_) {
            int meaningful_len = 64 - prev_leading_ - prev_trailing_;
            uint64_t meaningful_bits = xor_val >> prev_trailing_;
            uint64_t payload = (2ULL << meaningful_len) | 
                               (meaningful_bits & ((1ULL << meaningful_len) - 1ULL));
            return {payload, 2 + meaningful_len, false, prev_leading_, meaningful_len};
        }

        int meaningful_len = 64 - leading - trailing;
        uint64_t meaningful_bits = xor_val >> trailing;
        prev_leading_ = leading;
        prev_trailing_ = trailing;

        return {meaningful_bits, 2 + 5 + 6 + meaningful_len, true, leading, meaningful_len};
    }

private:
    uint64_t prev_val_bits_{0};
    int prev_leading_{64};
    int prev_trailing_{64};
    bool is_first_{true};
};
