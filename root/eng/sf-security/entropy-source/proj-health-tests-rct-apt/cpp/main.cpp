#include <cstdint>
#include <cstddef>
#include <span>
#include <expected>

namespace trng::health {

enum class Status : uint8_t {
    Ok,
    RctFailed,
    AptFailed
};

template <uint32_t RctCutoff = 35, uint32_t AptWindow = 512, uint32_t AptCutoff = 312>
class Sp80090bMonitor {
public:
    constexpr Sp80090bMonitor() noexcept = default;

    [[nodiscard]] std::expected<void, Status> process_sample(uint8_t sample) noexcept {
        if (alarm_latched_) {
            return std::unexpected(last_error_);
        }

        if (!initialized_) {
            rct_last_sample_ = sample;
            rct_rep_count_ = 1;
            apt_target_sample_ = sample;
            apt_match_count_ = 1;
            apt_window_index_ = 1;
            initialized_ = true;
            return {};
        }

        // 1. Repetition Count Test
        if (sample == rct_last_sample_) {
            if (++rct_rep_count_ >= RctCutoff) {
                return fail(Status::RctFailed);
            }
        } else {
            rct_last_sample_ = sample;
            rct_rep_count_ = 1;
        }

        // 2. Adaptive Proportion Test
        if (apt_window_index_ == 0) {
            apt_target_sample_ = sample;
            apt_match_count_ = 1;
            apt_window_index_ = 1;
        } else {
            if (sample == apt_target_sample_) {
                if (++apt_match_count_ >= AptCutoff) {
                    return fail(Status::AptFailed);
                }
            }
            if (++apt_window_index_ >= AptWindow) {
                apt_window_index_ = 0;
            }
        }

        return {};
    }

    [[nodiscard]] std::expected<void, Status> process_batch(std::span<const uint8_t> data) noexcept {
        for (const uint8_t byte : data) {
            if (auto res = process_sample(byte); !res) {
                return res;
            }
        }
        return {};
    }

    [[nodiscard]] constexpr bool is_healthy() const noexcept {
        return !alarm_latched_;
    }

    void reset() noexcept {
        initialized_ = false;
        alarm_latched_ = false;
        last_error_ = Status::Ok;
        rct_rep_count_ = 0;
        apt_window_index_ = 0;
    }

private:
    [[nodiscard]] std::expected<void, Status> fail(Status s) noexcept {
        alarm_latched_ = true;
        last_error_ = s;
        return std::unexpected(s);
    }

    uint8_t  rct_last_sample_{0};
    uint32_t rct_rep_count_{0};

    uint8_t  apt_target_sample_{0};
    uint32_t apt_match_count_{0};
    uint32_t apt_window_index_{0};

    bool     initialized_{false};
    bool     alarm_latched_{false};
    Status   last_error_{Status::Ok};
};

} // namespace trng::health
