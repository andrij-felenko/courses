#include <cstdint>
#include <cstddef>
#include <array>
#include <span>
#include <expected>
#include <chrono>

namespace thrust_rig {

enum class State : uint8_t {
    Idle,
    PreTare,
    Ramp,
    Settle,
    Acquire,
    PostTare,
    Cooldown,
    Emergency
};

enum class AbortReason : uint8_t {
    None,
    Overcurrent,
    MotorStall,
    ReverseThrust,
    Overheat,
    CommTimeout
};

struct BenchLimits {
    float max_current_a{45.0f};
    float max_temp_c{85.0f};
    std::chrono::milliseconds settle_duration{1500};
    std::chrono::milliseconds acquire_duration{2000};
    uint8_t step_increment_pct{10};
};

struct BenchRecord {
    std::chrono::milliseconds timestamp{0};
    float throttle_pct{0.0f};
    float thrust_grams{0.0f};
    float voltage_v{0.0f};
    float current_a{0.0f};
    float power_w{0.0f};
    float rpm{0.0f};
    float eff_grams_per_watt{0.0f};
    float temp_c{25.0f};
};

// Апаратний інтерфейс (HAL абстракція)
class IHardwareDriver {
public:
    virtual ~IHardwareDriver() = default;
    virtual void write_throttle(float pct) = 0;
    virtual auto read_thrust_raw_grams() -> std::expected<float, AbortReason> = 0;
    virtual auto read_bus_power() -> std::expected<std::pair<float, float>, AbortReason> = 0; // {V, A}
    virtual auto read_rotor_rpm() -> std::expected<float, AbortReason> = 0;
    virtual auto read_sensor_temp_c() -> std::expected<float, AbortReason> = 0;
    virtual auto get_uptime_ms() const -> std::chrono::milliseconds = 0;
    virtual void stream_record(const BenchRecord& record) = 0;
};

template <size_t MaxSteps = 11>
class RigController {
public:
    explicit constexpr RigController(const BenchLimits& limits, IHardwareDriver& hal)
        : limits_(limits), hal_(hal) {
        total_steps_ = (100 / limits_.step_increment_pct) + 1;
        if (total_steps_ > MaxSteps) total_steps_ = MaxSteps;
    }

    void start_test() noexcept {
        if (state_ != State::Idle) return;
        current_step_idx_ = 0;
        current_throttle_ = 0.0f;
        target_throttle_ = 0.0f;
        sample_count_ = 0;
        acc_thrust_ = 0.0f;
        acc_temp_ = 0.0f;
        state_entry_time_ = hal_.get_uptime_ms();
        state_ = State::PreTare;
        hal_.write_throttle(0.0f);
    }

    void abort_test(AbortReason reason) noexcept {
        hal_.write_throttle(0.0f);
        current_throttle_ = 0.0f;
        state_ = State::Emergency;
        abort_reason_ = reason;
    }

    void update() noexcept {
        const auto now = hal_.get_uptime_ms();
        const auto elapsed = now - state_entry_time_;

        // Читання апаратних сенсорів
        const auto thrust_res = hal_.read_thrust_raw_grams();
        const auto power_res = hal_.read_bus_power();
        const auto rpm_res = hal_.read_rotor_rpm();
        const auto temp_res = hal_.read_sensor_temp_c();

        if (!thrust_res || !power_res || !rpm_res || !temp_res) {
            abort_test(AbortReason::CommTimeout);
            return;
        }

        const float raw_thrust = *thrust_res;
        const auto [v, i] = *power_res;
        const float rpm = *rpm_res;
        const float temp_c = *temp_res;

        // Безпекові перевірки
        if (state_ != State::Idle && state_ != State::Emergency) {
            if (!check_safety(v, i, raw_thrust - pre_tare_offset_g_, rpm, temp_c)) {
                return;
            }
        }

        switch (state_) {
            case State::Idle:
            case State::Emergency:
                hal_.write_throttle(0.0f);
                break;

            case State::PreTare:
                acc_thrust_ += raw_thrust;
                acc_temp_ += temp_c;
                sample_count_++;
                if (elapsed >= std::chrono::milliseconds{1500} && sample_count_ > 0) {
                    pre_tare_offset_g_ = acc_thrust_ / static_cast<float>(sample_count_);
                    start_temp_c_ = acc_temp_ / static_cast<float>(sample_count_);
                    current_step_idx_ = 0;
                    target_throttle_ = 0.0f;
                    transition_to(State::Ramp, now);
                }
                break;

            case State::Ramp:
                if (current_throttle_ < target_throttle_) {
                    current_throttle_ += 0.5f;
                    if (current_throttle_ > target_throttle_) current_throttle_ = target_throttle_;
                }
                hal_.write_throttle(current_throttle_);
                if (current_throttle_ >= target_throttle_) {
                    transition_to(State::Settle, now);
                }
                break;

            case State::Settle:
                if (elapsed >= limits_.settle_duration) {
                    reset_accumulators();
                    transition_to(State::Acquire, now);
                }
                break;

            case State::Acquire:
                acc_thrust_ += (raw_thrust - pre_tare_offset_g_);
                acc_voltage_ += v;
                acc_current_ += i;
                acc_rpm_ += rpm;
                acc_temp_ += temp_c;
                sample_count_++;

                if (elapsed >= limits_.acquire_duration && sample_count_ > 0) {
                    auto& rec = results_[current_step_idx_];
                    rec.timestamp = now;
                    rec.throttle_pct = current_throttle_;
                    rec.thrust_grams = acc_thrust_ / static_cast<float>(sample_count_);
                    rec.voltage_v = acc_voltage_ / static_cast<float>(sample_count_);
                    rec.current_a = acc_current_ / static_cast<float>(sample_count_);
                    rec.power_w = rec.voltage_v * rec.current_a;
                    rec.rpm = acc_rpm_ / static_cast<float>(sample_count_);
                    rec.temp_c = acc_temp_ / static_cast<float>(sample_count_);
                    rec.eff_grams_per_watt = (rec.power_w > 0.05f) ? (rec.thrust_grams / rec.power_w) : 0.0f;

                    hal_.stream_record(rec);

                    current_step_idx_++;
                    if (current_step_idx_ < total_steps_) {
                        target_throttle_ = static_cast<float>(current_step_idx_ * limits_.step_increment_pct);
                        if (target_throttle_ > 100.0f) target_throttle_ = 100.0f;
                        transition_to(State::Ramp, now);
                    } else {
                        hal_.write_throttle(0.0f);
                        current_throttle_ = 0.0f;
                        reset_accumulators();
                        transition_to(State::PostTare, now);
                    }
                }
                break;

            case State::PostTare:
                acc_thrust_ += raw_thrust;
                acc_temp_ += temp_c;
                sample_count_++;
                if (elapsed >= std::chrono::milliseconds{1500} && sample_count_ > 0) {
                    post_tare_offset_g_ = acc_thrust_ / static_cast<float>(sample_count_);
                    end_temp_c_ = acc_temp_ / static_cast<float>(sample_count_);
                    transition_to(State::Cooldown, now);
                }
                break;

            case State::Cooldown:
                if (elapsed >= std::chrono::seconds{10}) {
                    transition_to(State::Idle, now);
                }
                break;
        }
    }

    [[nodiscard]] constexpr auto get_state() const noexcept -> State { return state_; }
    [[nodiscard]] constexpr auto get_abort_reason() const noexcept -> AbortReason { return abort_reason_; }
    [[nodiscard]] auto get_results() const noexcept -> std::span<const BenchRecord> {
        return {results_.data(), current_step_idx_};
    }

private:
    void transition_to(State next, std::chrono::milliseconds now) noexcept {
        state_ = next;
        state_entry_time_ = now;
    }

    void reset_accumulators() noexcept {
        acc_thrust_ = 0.0f;
        acc_voltage_ = 0.0f;
        acc_current_ = 0.0f;
        acc_rpm_ = 0.0f;
        acc_temp_ = 0.0f;
        sample_count_ = 0;
    }

    bool check_safety(float v, float i, float thrust, float rpm, float temp) noexcept {
        if (i > limits_.max_current_a) {
            abort_test(AbortReason::Overcurrent);
            return false;
        }
        if (temp > limits_.max_temp_c) {
            abort_test(AbortReason::Overheat);
            return false;
        }
        if (current_throttle_ > 25.0f && rpm < 300.0f && i > 2.5f) {
            abort_test(AbortReason::MotorStall);
            return false;
        }
        if (current_throttle_ > 30.0f && thrust < -25.0f) {
            abort_test(AbortReason::ReverseThrust);
            return false;
        }
        return true;
    }

    BenchLimits limits_;
    IHardwareDriver& hal_;
    State state_{State::Idle};
    AbortReason abort_reason_{AbortReason::None};
    
    size_t current_step_idx_{0};
    size_t total_steps_{MaxSteps};
    float target_throttle_{0.0f};
    float current_throttle_{0.0f};
    
    std::chrono::milliseconds state_entry_time_{0};
    float pre_tare_offset_g_{0.0f};
    float post_tare_offset_g_{0.0f};
    float start_temp_c_{25.0f};
    float end_temp_c_{25.0f};
    
    std::array<BenchRecord, MaxSteps> results_{};
    
    float acc_thrust_{0.0f};
    float acc_voltage_{0.0f};
    float acc_current_{0.0f};
    float acc_rpm_{0.0f};
    float acc_temp_{0.0f};
    size_t sample_count_{0};
};

} // namespace thrust_rig
