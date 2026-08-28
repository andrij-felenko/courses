#include <chrono>
#include <atomic>
#include <cstdint>
#include <algorithm>

class TimeEngine {
public:
    using Microseconds = std::chrono::microseconds;
    using TimePointUtc = std::chrono::time_point<std::chrono::system_clock, Microseconds>;
    using TimePointMono = std::chrono::time_point<std::chrono::steady_clock, Microseconds>;

    static constexpr int32_t MaxSlewPpm = 500;
    static constexpr Microseconds StepThreshold = std::chrono::seconds(2);
    static constexpr int64_t PpmScale = 1'000'000;

    explicit TimeEngine(Microseconds initial_utc, int32_t quartz_drift_ppm = 0) noexcept
        : sequence_(0),
          last_hw_ticks_(read_hw_ticks()),
          monotonic_accum_us_(0),
          epoch_offset_us_(initial_utc.count()),
          slew_remaining_us_(0),
          slew_rate_ppm_(0),
          last_slew_update_us_(0),
          static_drift_ppm_(quartz_drift_ppm) {}

    // Отримання неперервного монотонного часу для вимірювань і дедлайнів
    [[nodiscard]] TimePointMono get_monotonic_time() const noexcept {
        uint32_t seq;
        uint64_t mono_us;
        do {
            seq = sequence_.load(std::memory_order_acquire);
            while (seq & 1) {
                seq = sequence_.load(std::memory_order_acquire);
            }

            uint32_t current_ticks = read_hw_ticks();
            uint32_t delta = current_ticks - last_hw_ticks_;
            mono_us = monotonic_accum_us_ + delta;

        } while (sequence_.load(std::memory_order_relaxed) != seq);

        return TimePointMono(Microseconds(mono_us));
    }

    // Отримання настінного часу (календар UTC)
    [[nodiscard]] TimePointUtc get_wall_clock_utc() const noexcept {
        uint32_t seq;
        int64_t wall_us;
        do {
            seq = sequence_.load(std::memory_order_acquire);
            while (seq & 1) {
                seq = sequence_.load(std::memory_order_acquire);
            }

            auto mono = get_monotonic_time();
            wall_us = mono.time_since_epoch().count() + epoch_offset_us_;

        } while (sequence_.load(std::memory_order_relaxed) != seq);

        return TimePointUtc(Microseconds(wall_us));
    }

    // Синхронізація від джерела еталонного часу (NTP/GNSS)
    void sync_time(TimePointUtc target_utc) noexcept {
        uint32_t seq = sequence_.load(std::memory_order_relaxed);
        sequence_.store(seq + 1, std::memory_order_release);

        update_internal();

        int64_t target_us = target_utc.time_since_epoch().count();
        int64_t current_utc_us = monotonic_accum_us_ + epoch_offset_us_;
        int64_t phase_error = target_us - current_utc_us;

        if (std::abs(phase_error) > StepThreshold.count()) {
            // Велике відхилення: стрибок (step)
            epoch_offset_us_ += phase_error;
            slew_remaining_us_ = 0;
            slew_rate_ppm_ = 0;
        } else {
            // Мале відхилення: плавне підтягування (slew)
            slew_remaining_us_ = phase_error;
            slew_rate_ppm_ = (phase_error > 0) ? MaxSlewPpm : -MaxSlewPpm;
            last_slew_update_us_ = monotonic_accum_us_;
        }

        sequence_.store(seq + 2, std::memory_order_release);
    }

private:
    static uint32_t read_hw_ticks() noexcept {
        extern uint32_t hw_timer_get_32bit_ticks(void);
        return hw_timer_get_32bit_ticks();
    }

    void update_internal() noexcept {
        uint32_t current_ticks = read_hw_ticks();
        uint32_t delta = current_ticks - last_hw_ticks_;
        last_hw_ticks_ = current_ticks;

        monotonic_accum_us_ += delta;
        uint64_t now_mono = monotonic_accum_us_;

        if (slew_remaining_us_ != 0) {
            uint64_t dt = now_mono - last_slew_update_us_;
            if (dt > 0) {
                int64_t delta_slew = (static_cast<int64_t>(dt) * slew_rate_ppm_) / PpmScale;

                if ((slew_remaining_us_ > 0 && delta_slew >= slew_remaining_us_) ||
                    (slew_remaining_us_ < 0 && delta_slew <= slew_remaining_us_)) {
                    epoch_offset_us_ += slew_remaining_us_;
                    slew_remaining_us_ = 0;
                    slew_rate_ppm_ = 0;
                } else {
                    epoch_offset_us_ += delta_slew;
                    slew_remaining_us_ -= delta_slew;
                }
                last_slew_update_us_ = now_mono;
            }
        }
    }

    mutable std::atomic<uint32_t> sequence_;
    uint32_t last_hw_ticks_;
    uint64_t monotonic_accum_us_;
    int64_t  epoch_offset_us_;
    int64_t  slew_remaining_us_;
    int32_t  slew_rate_ppm_;
    uint64_t last_slew_update_us_;
    int32_t  static_drift_ppm_;
};
