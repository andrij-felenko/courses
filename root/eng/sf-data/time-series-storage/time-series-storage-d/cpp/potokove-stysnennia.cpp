#include <cstdint>
#include <utility>

class TimestampEncoder {
public:
    struct EncodedBits {
        uint64_t bits{0};
        int bit_length{0};
    };

    EncodedBits encode(uint64_t current_time) noexcept {
        if (sample_count_ == 0) {
            prev_time_ = current_time;
            sample_count_++;
            return {current_time, 64};
        }

        uint64_t delta = current_time - prev_time_;
        if (sample_count_ == 1) {
            prev_delta_ = delta;
            prev_time_ = current_time;
            sample_count_++;
            return {delta, 14};
        }

        int64_t dod = static_cast<int64_t>(delta) - static_cast<int64_t>(prev_delta_);
        prev_delta_ = delta;
        prev_time_ = current_time;
        sample_count_++;

        if (dod == 0) {
            return {0ULL, 1}; // 1 біт '0'
        }
        if (dod >= -63 && dod <= 64) {
            uint64_t payload = (2ULL << 7) | (static_cast<uint64_t>(dod) & 0x7FULL);
            return {payload, 9}; // Префікс '10' + 7 бітів
        }
        if (dod >= -255 && dod <= 256) {
            uint64_t payload = (6ULL << 9) | (static_cast<uint64_t>(dod) & 0x1FFULL);
            return {payload, 12}; // Префікс '110' + 9 бітів
        }
        if (dod >= -2047 && dod <= 2048) {
            uint64_t payload = (14ULL << 12) | (static_cast<uint64_t>(dod) & 0xFFFULL);
            return {payload, 16}; // Префікс '1110' + 12 бітів
        }

        uint64_t payload = (15ULL << 32) | static_cast<uint32_t>(dod);
        return {payload, 36}; // Префікс '1111' + 32 біти
    }

    [[nodiscard]] size_t count() const noexcept { return sample_count_; }

private:
    uint64_t prev_time_{0};
    uint64_t prev_delta_{0};
    size_t sample_count_{0};
};
