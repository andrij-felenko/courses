#include <cstdint>
#include <cmath>
#include <chrono>
#include <algorithm>
#include <concepts>

class ClockServo {
public:
    enum class State {
        Unlocked,
        Locking,
        Locked,
        Holdover
    };

    struct Timestamp {
        std::uint64_t sec{0};
        std::uint64_t nsec{0};
        std::uint32_t sub_nsec{0}; // Q32 дробова частина наносекунди
    };

    struct TuningParameters {
        double kp{0.10};          // 1/с
        double ki{0.005};         // 1/с^2
        double max_slew_ppm{500.0};
        std::int64_t step_threshold_ns{100'000'000}; // 100 мс
        std::uint32_t pps_timeout_ticks{2};
    };

    explicit ClockServo(double nominal_freq_hz, TuningParameters params = {})
        : nominal_tick_ns_{1e9 / nominal_freq_hz}, params_{params} {}

    void advance_ticks(std::uint64_t current_hw_ticks) noexcept {
        const std::uint64_t delta_ticks = current_hw_ticks - last_hw_ticks_;
        last_hw_ticks_ = current_hw_ticks;

        const double rate_multiplier = 1.0 + (current_slew_ppm_ * 1e-6);
        const double elapsed_ns_exact = static_cast<double>(delta_ticks) * nominal_tick_ns_ * rate_multiplier;

        const auto elapsed_ns_int = static_cast<std::uint64_t>(elapsed_ns_exact);
        const auto elapsed_sub_ns = static_cast<std::uint32_t>(
            (elapsed_ns_exact - static_cast<double>(elapsed_ns_int)) * subns_scale_
        );

        const std::uint64_t total_sub = static_cast<std::uint64_t>(time_.sub_nsec) + elapsed_sub_ns;
        time_.sub_nsec = static_cast<std::uint32_t>(total_sub & (subns_scale_ - 1));
        const std::uint64_t carry_ns = total_sub >> subns_shift_;

        const std::uint64_t total_ns = time_.nsec + elapsed_ns_int + carry_ns;
        time_.sec += total_ns / 1'000'000'000ULL;
        time_.nsec = total_ns % 1'000'000'000ULL;
    }

    void on_pps(std::uint64_t pps_hw_ticks, std::uint64_t ref_sec) noexcept {
        advance_ticks(pps_hw_ticks);
        missed_pps_count_ = 0;

        const auto sec_diff = static_cast<std::int64_t>(ref_sec) - static_cast<std::int64_t>(time_.sec);
        const std::int64_t error_ns = (sec_diff * 1'000'000'000LL) - static_cast<std::int64_t>(time_.nsec);
        last_phase_error_ns_ = error_ns;

        if (std::abs(error_ns) > params_.step_threshold_ns) {
            time_.sec = ref_sec;
            time_.nsec = 0;
            time_.sub_nsec = 0;
            integrated_drift_ppm_ = 0.0;
            current_slew_ppm_ = 0.0;
            state_ = State::Locking;
            consecutive_locked_secs_ = 0;
            return;
        }

        const double p_term = params_.kp * static_cast<double>(error_ns) * 1e-3;
        integrated_drift_ppm_ += params_.ki * static_cast<double>(error_ns) * 1e-3;

        // Anti-windup
        integrated_drift_ppm_ = std::clamp(integrated_drift_ppm_, -params_.max_slew_ppm, params_.max_slew_ppm);

        const double total_slew = p_term + integrated_drift_ppm_;
        current_slew_ppm_ = std::clamp(total_slew, -params_.max_slew_ppm, params_.max_slew_ppm);

        if (std::abs(error_ns) < 100) {
            ++consecutive_locked_secs_;
            if (consecutive_locked_secs_ >= 5) {
                state_ = State::Locked;
            }
        } else {
            consecutive_locked_secs_ = 0;
            if (state_ == State::Locked) {
                state_ = State::Locking;
            }
        }
    }

    void on_pps_timeout() noexcept {
        ++missed_pps_count_;
        if (missed_pps_count_ >= params_.pps_timeout_ticks) {
            state_ = State::Holdover;
            current_slew_ppm_ = integrated_drift_ppm_;
        }
    }

    [[nodiscard]] Timestamp now() const noexcept { return time_; }
    [[nodiscard]] std::int64_t phase_error_ns() const noexcept { return last_phase_error_ns_; }
    [[nodiscard]] double estimated_drift_ppm() const noexcept { return integrated_drift_ppm_; }
    [[nodiscard]] State state() const noexcept { return state_; }

private:
    static constexpr std::uint32_t subns_shift_{32};
    static constexpr double subns_scale_{4294967296.0}; // 2^32

    Timestamp time_{};
    std::uint64_t last_hw_ticks_{0};
    double nominal_tick_ns_{0.0};
    TuningParameters params_{};

    double integrated_drift_ppm_{0.0};
    double current_slew_ppm_{0.0};
    std::int64_t last_phase_error_ns_{0};
    State state_{State::Unlocked};
    std::uint32_t consecutive_locked_secs_{0};
    std::uint32_t missed_pps_count_{0};
};
