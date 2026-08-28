#include <cstdint>
#include <optional>
#include <algorithm>

class RocTracker {
public:
    struct Estimate {
        std::uint64_t index;
        std::uint32_t roc;
    };

    [[nodiscard]] Estimate estimate_index(std::uint16_t seq) const noexcept {
        if (!initialized_) {
            return { static_cast<std::uint64_t>(seq), 0 };
        }

        std::uint32_t roc_est = roc_;
        if (s_l_ < 32768) {
            if (static_cast<std::uint16_t>(seq - s_l_) > 32768) {
                roc_est = (roc_ > 0) ? (roc_ - 1) : 0;
            }
        } else {
            if (static_cast<std::uint16_t>(s_l_ - seq) > 32768) {
                roc_est = roc_ + 1;
            }
        }

        const std::uint64_t idx = (static_cast<std::uint64_t>(roc_est) << 16) | seq;
        return { idx, roc_est };
    }

    void update(std::uint16_t seq, std::uint32_t roc_est) noexcept {
        if (!initialized_) {
            s_l_ = seq;
            roc_ = roc_est;
            initialized_ = true;
            return;
        }

        const std::uint64_t new_idx = (static_cast<std::uint64_t>(roc_est) << 16) | seq;
        const std::uint64_t cur_idx = (static_cast<std::uint64_t>(roc_) << 16) | s_l_;

        if (new_idx > cur_idx) {
            s_l_ = seq;
            roc_ = roc_est;
        }
    }

    [[nodiscard]] bool is_initialized() const noexcept { return initialized_; }
    [[nodiscard]] std::uint32_t current_roc() const noexcept { return roc_; }
    [[nodiscard]] std::uint16_t highest_seq() const noexcept { return s_l_; }

private:
    std::uint32_t roc_{0};
    std::uint16_t s_l_{0};
    bool initialized_{false};
};
