#include <zephyr/kernel.h>
#include <atomic>
#include <cstdint>

enum class AlarmState : uint8_t {
    Normal = 0,
    Unacknowledged,
    Acknowledged,
    ReturnToNormalUnack,
    Shelved,
    Suppressed,
    OutOfService
};

enum class AlarmPriority : uint8_t {
    Low = 0,
    Medium,
    High,
    Emergency
};

class AlarmChannel {
public:
    AlarmChannel(float threshold, float deadband, uint16_t on_delay, 
                 uint16_t off_delay, AlarmPriority priority)
        : threshold_high_(threshold), deadband_(deadband),
          on_delay_samples_(on_delay), off_delay_samples_(off_delay),
          priority_(priority), state_(AlarmState::Normal),
          on_counter_(0), off_counter_(0), trip_timestamp_us_(0),
          status_flags_(0) {}

    void ProcessSample(float raw_val, uint64_t now_us) {
        if (state_ == AlarmState::OutOfService || state_ == AlarmState::Suppressed) {
            return;
        }

        const bool physical_exceeded = (raw_val >= threshold_high_);
        const bool physical_cleared = (raw_val < (threshold_high_ - deadband_));

        if (physical_exceeded) {
            off_counter_ = 0;
            if (on_counter_ < on_delay_samples_) {
                on_counter_++;
            }
        } else if (physical_cleared) {
            on_counter_ = 0;
            if (off_counter_ < off_delay_samples_) {
                off_counter_++;
            }
        }

        const bool condition_active = (on_counter_ >= on_delay_samples_);
        const bool condition_normal = (off_counter_ >= off_delay_samples_);

        switch (state_) {
            case AlarmState::Normal:
                if (condition_active) {
                    state_ = AlarmState::Unacknowledged;
                    trip_timestamp_us_ = now_us;
                    status_flags_.fetch_or(kFlagActive, std::memory_order_relaxed);
                }
                break;

            case AlarmState::Unacknowledged:
                if (condition_normal) {
                    state_ = AlarmState::ReturnToNormalUnack;
                    status_flags_.fetch_and(~kFlagActive, std::memory_order_relaxed);
                }
                break;

            case AlarmState::Acknowledged:
                if (condition_normal) {
                    state_ = AlarmState::Normal;
                    status_flags_.fetch_and(~kFlagActive, std::memory_order_relaxed);
                }
                break;

            case AlarmState::ReturnToNormalUnack:
                if (condition_active) {
                    state_ = AlarmState::Unacknowledged;
                    status_flags_.fetch_or(kFlagActive, std::memory_order_relaxed);
                }
                break;

            default:
                break;
        }
    }

    void Acknowledge() {
        if (state_ == AlarmState::Unacknowledged) {
            state_ = AlarmState::Acknowledged;
        } else if (state_ == AlarmState::ReturnToNormalUnack) {
            state_ = AlarmState::Normal;
        }
    }

    AlarmState GetState() const { return state_; }
    uint64_t GetTripTimestampUs() const { return trip_timestamp_us_; }

private:
    static constexpr uint32_t kFlagActive = (1U << 0);
    static constexpr uint32_t kFlagFirstOut = (1U << 1);

    float threshold_high_;
    float deadband_;
    uint16_t on_delay_samples_;
    uint16_t off_delay_samples_;
    AlarmPriority priority_;
    AlarmState state_;
    uint16_t on_counter_;
    uint16_t off_counter_;
    uint64_t trip_timestamp_us_;
    std::atomic<uint32_t> status_flags_;
};
