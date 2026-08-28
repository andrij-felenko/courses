#include <cstdint>
#include <chrono>
#include <algorithm>

namespace embedded::power {

enum class FuseState : uint8_t {
    Off = 0,
    SoftStart,
    Operational,
    CurrentLimit,
    Fault
};

enum class FaultReason : uint8_t {
    None = 0,
    ShortCircuit,
    ThermalI2t,
    SoaViolation,
    StartupTimeout,
    Undervoltage
};

struct FuseConfig {
    float vin_min_v{4.5f};
    float nominal_current_a{5.0f};
    float short_circuit_current_a{25.0f};
    float i2t_energy_limit_a2s{12.5f};
    float max_linear_power_w{30.0f};
    float soft_start_step_v{0.2f};
    uint32_t startup_timeout_ms{50};
    uint32_t cooldown_time_ms{1000};
    bool auto_retry{true};
};

class SmartEFuseController {
public:
    explicit SmartEFuseController(const FuseConfig& config) noexcept
        : config_(config), state_(FuseState::Off), last_fault_(FaultReason::None) {}

    void ProcessTick(bool enable_request, float v_in, float v_out, float i_load, std::chrono::milliseconds dt) noexcept {
        const float dt_sec = std::chrono::duration<float>(dt).count();
        const float v_ds = (v_in > v_out) ? (v_in - v_out) : 0.0f;

        // Захист від зниження напруги живлення (UVLO)
        if (v_in < config_.vin_min_v && state_ != FuseState::Off) {
            TripFault(FaultReason::Undervoltage);
            return;
        }

        switch (state_) {
        case FuseState::Off:
            if (enable_request && v_in >= config_.vin_min_v) {
                state_ = FuseState::SoftStart;
                v_gate_current_v_ = 0.0f;
                state_elapsed_time_ = std::chrono::milliseconds{0};
                accumulated_i2t_ = 0.0f;
                linear_mode_energy_j_ = 0.0f;
            }
            break;

        case FuseState::SoftStart: {
            state_elapsed_time_ += dt;

            // Субмікросекундний захист від КЗ під час пуску
            if (i_load >= config_.short_circuit_current_a) {
                TripFault(FaultReason::ShortCircuit);
                return;
            }

            // Контроль теплового стресу кристала в лінійному режимі (SOA)
            const float power_now = v_ds * i_load;
            linear_mode_energy_j_ += power_now * dt_sec;
            if (power_now > config_.max_linear_power_w && linear_mode_energy_j_ > 2.0f) {
                TripFault(FaultReason::SoaViolation);
                return;
            }

            // Плавний підйом напруги затвора
            v_gate_current_v_ = std::min(v_gate_current_v_ + config_.soft_start_step_v, target_gate_v_);
            ApplyGateVoltage(v_gate_current_v_);

            if (v_out >= (v_in * 0.90f)) {
                state_ = FuseState::Operational;
                v_gate_current_v_ = target_gate_v_;
                ApplyGateVoltage(v_gate_current_v_);
                state_elapsed_time_ = std::chrono::milliseconds{0};
                linear_mode_energy_j_ = 0.0f;
            } else if (state_elapsed_time_.count() > config_.startup_timeout_ms) {
                TripFault(FaultReason::StartupTimeout);
            }
            break;
        }

        case FuseState::Operational:
            // 1. Надшвидке відсікання КЗ
            if (i_load >= config_.short_circuit_current_a) {
                TripFault(FaultReason::ShortCircuit);
                return;
            }

            // 2. Тепловий інтеграл надструму I²t
            if (i_load > config_.nominal_current_a) {
                const float excess = i_load - config_.nominal_current_a;
                accumulated_i2t_ += (excess * excess) * dt_sec;

                if (accumulated_i2t_ >= config_.i2t_energy_limit_a2s) {
                    TripFault(FaultReason::ThermalI2t);
                    return;
                }
            } else {
                // Охолодження при нормальному струмі
                accumulated_i2t_ = std::max(0.0f, accumulated_i2t_ - accumulated_i2t_ * 0.1f * dt_sec);
            }

            if (!enable_request) {
                FastShutdown();
                state_ = FuseState::Off;
            }
            break;

        case FuseState::CurrentLimit:
            state_elapsed_time_ += dt;
            if (v_ds * i_load > config_.max_linear_power_w) {
                TripFault(FaultReason::SoaViolation);
            }
            break;

        case FuseState::Fault:
            state_elapsed_time_ += dt;

            if (config_.auto_retry && enable_request) {
                if (state_elapsed_time_.count() >= config_.cooldown_time_ms) {
                    retry_counter_++;
                    state_ = FuseState::SoftStart;
                    v_gate_current_v_ = 0.0f;
                    state_elapsed_time_ = std::chrono::milliseconds{0};
                    accumulated_i2t_ = 0.0f;
                    linear_mode_energy_j_ = 0.0f;
                }
            } else if (!enable_request) {
                state_ = FuseState::Off;
                last_fault_ = FaultReason::None;
                retry_counter_ = 0;
            }
            break;
        }
    }

    [[nodiscard]] FuseState GetState() const noexcept { return state_; }
    [[nodiscard]] FaultReason GetLastFault() const noexcept { return last_fault_; }
    [[nodiscard]] float GetThermalStressPercent() const noexcept {
        return (accumulated_i2t_ / config_.i2t_energy_limit_a2s) * 100.0f;
    }

private:
    void TripFault(FaultReason reason) noexcept {
        FastShutdown();
        state_ = FuseState::Fault;
        last_fault_ = reason;
        state_elapsed_time_ = std::chrono::milliseconds{0};
    }

    static void ApplyGateVoltage(float v_gate) noexcept;
    static void FastShutdown() noexcept;

    FuseConfig config_;
    FuseState state_{FuseState::Off};
    FaultReason last_fault_{FaultReason::None};

    float v_gate_current_v_{0.0f};
    static constexpr float target_gate_v_{10.0f};
    float accumulated_i2t_{0.0f};
    float linear_mode_energy_j_{0.0f};

    std::chrono::milliseconds state_elapsed_time_{0};
    uint32_t retry_counter_{0};
};

} // namespace embedded::power
