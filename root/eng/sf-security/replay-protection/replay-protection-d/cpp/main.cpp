#include <cstdint>

class ReplayFilter {
public:
    static constexpr uint64_t WindowSize = 64;

    [[nodiscard]] bool check(uint64_t seq) const noexcept {
        if (seq == 0) return false;
        if (seq > seq_max_) return true;
        const uint64_t diff = seq_max_ - seq;
        if (diff >= WindowSize) return false;
        return (bitmap_ & (uint64_t{1} << diff)) == 0;
    }

    void commit(uint64_t seq) noexcept {
        if (seq > seq_max_) {
            const uint64_t diff = seq - seq_max_;
            bitmap_ = (diff < WindowSize) ? ((bitmap_ << diff) | 1) : 1;
            seq_max_ = seq;
        } else {
            const uint64_t diff = seq_max_ - seq;
            if (diff < WindowSize) {
                bitmap_ |= (uint64_t{1} << diff);
            }
        }
    }

private:
    uint64_t seq_max_{0};
    uint64_t bitmap_{0};
};
