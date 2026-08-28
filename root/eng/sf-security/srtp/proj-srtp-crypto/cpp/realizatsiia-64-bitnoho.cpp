#include <cstdint>
#include <optional>

enum class ReplayStatus {
    Ok,
    Duplicate,
    Old
};

class ReplayWindow {
public:
    static constexpr std::uint64_t WindowSize = 64;

    [[nodiscard]] ReplayStatus check(std::uint64_t index) const noexcept {
        if (!initialized_) {
            return ReplayStatus::Ok;
        }

        if (index > max_index_) {
            return ReplayStatus::Ok;
        }

        const std::uint64_t diff = max_index_ - index;
        if (diff >= WindowSize) {
            return ReplayStatus::Old;
        }

        if ((window_mask_ & (1ULL << diff)) != 0) {
            return ReplayStatus::Duplicate;
        }

        return ReplayStatus::Ok;
    }

    void update(std::uint64_t index) noexcept {
        if (!initialized_) {
            max_index_ = index;
            window_mask_ = 1ULL;
            initialized_ = true;
            return;
        }

        if (index > max_index_) {
            const std::uint64_t shift = index - max_index_;
            if (shift < WindowSize) {
                window_mask_ <<= shift;
            } else {
                window_mask_ = 0;
            }
            window_mask_ |= 1ULL;
            max_index_ = index;
        } else {
            const std::uint64_t diff = max_index_ - index;
            if (diff < WindowSize) {
                window_mask_ |= (1ULL << diff);
            }
        }
    }

    [[nodiscard]] std::uint64_t max_index() const noexcept { return max_index_; }

private:
    std::uint64_t max_index_{0};
    std::uint64_t window_mask_{0};
    bool initialized_{false};
};
