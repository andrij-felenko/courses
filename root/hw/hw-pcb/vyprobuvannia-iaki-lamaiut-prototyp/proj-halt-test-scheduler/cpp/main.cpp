#include <iostream>
#include <vector>
#include <span>
#include <array>
#include <chrono>
#include <cmath>
#include <optional>
#include <expected>
#include <string_view>
#include <algorithm>

using namespace std::chrono_literals;

enum class StressType {
    TemperatureCold,
    TemperatureHot,
    VibrationRandom,
    Combined
};

enum class HaltState {
    Idle,
    Ramp,
    Dwell,
    RecoveryCheck,
    EmergencyAbort,
    Complete
};

enum class FaultType : uint32_t {
    None               = 0,
    VoltageSag         = 1 << 0,
    Overcurrent        = 1 << 1,
    ThermalRunaway     = 1 << 2,
    CommTimeout        = 1 << 3,
    CrcErrorBurst      = 1 << 4,
    VibrationOverload  = 1 << 5
};

constexpr FaultType operator|(FaultType a, FaultType b) noexcept {
    return static_cast<FaultType>(static_cast<uint32_t>(a) | static_cast<uint32_t>(b));
}

constexpr bool has_fault(FaultType mask, FaultType check) noexcept {
    return (static_cast<uint32_t>(mask) & static_cast<uint32_t>(check)) != 0;
}

constexpr size_t MaxChannels = 4;
constexpr size_t RingBufferSize = 256;

struct TelemetrySnapshot {
    std::chrono::milliseconds timestamp{0ms};
    float chamber_temp_c{25.0f};
    float dut_hotspot_temp_c{25.0f};
    std::array<float, MaxChannels> supply_voltage_v{3.3f, 5.0f, 12.0f, 0.0f};
    std::array<float, MaxChannels> supply_current_ma{100.0f, 200.0f, 50.0f, 0.0f};
    float vibration_g_rms{0.0f};
    uint16_t comm_crc_errors{0};
    bool comm_alive{true};
    FaultType fault_mask{FaultType::None};
};

struct StepConfig {
    StressType type{StressType::TemperatureHot};
    float target_value{85.0f};
    float ramp_rate_per_min{60.0f};
    std::chrono::seconds dwell_time{600s};
    float voltage_margin_pct{0.0f};
};

struct SafetyThresholds {
    std::array<float, MaxChannels> max_allowed_current_ma{1500.0f, 2000.0f, 1000.0f, 500.0f};
    std::array<float, MaxChannels> min_allowed_voltage_v{2.97f, 4.5f, 10.8f, 0.0f};
    std::array<float, MaxChannels> max_allowed_voltage_v{3.63f, 5.5f, 13.2f, 0.0f};
    float max_dut_temp_c{150.0f};
    float max_temp_slew_c_per_sec{5.0f};
    float max_vibration_g_rms{55.0f};
    uint32_t max_consecutive_comm_failures{5};
};

class TelemetryRingBuffer {
public:
    void push(const TelemetrySnapshot& snap) noexcept {
        if (frozen_) return;
        buffer_[head_] = snap;
        head_ = (head_ + 1) % RingBufferSize;
        if (count_ < RingBufferSize) {
            count_++;
        }
    }

    void freeze() noexcept { frozen_ = true; }
    [[nodiscard]] bool is_frozen() const noexcept { return frozen_; }
    [[nodiscard]] size_t size() const noexcept { return count_; }

    [[nodiscard]] std::optional<TelemetrySnapshot> latest() const noexcept {
        if (count_ == 0) return std::nullopt;
        size_t idx = (head_ == 0) ? (RingBufferSize - 1) : (head_ - 1);
        return buffer_[idx];
    }

private:
    std::array<TelemetrySnapshot, RingBufferSize> buffer_{};
    size_t head_{0};
    size_t count_{0};
    bool frozen_{false};
};

class ChamberPowerGuard {
public:
    explicit ChamberPowerGuard(bool& relay_state) : relay_state_(relay_state) {
        relay_state_ = true; // Увімкнути живлення камери
    }
    ~ChamberPowerGuard() {
        relay_state_ = false; // Безпечне вимкнення при виході з області
    }
    ChamberPowerGuard(const ChamberPowerGuard&) = delete;
    ChamberPowerGuard& operator=(const ChamberPowerGuard&) = delete;

private:
    bool& relay_state_;
};

class HaltScheduler {
public:
    explicit HaltScheduler(SafetyThresholds safety) noexcept 
        : safety_(std::move(safety)), state_(HaltState::Idle) {}

    void add_step(StepConfig step) {
        scenario_.push_back(step);
    }

    [[nodiscard]] FaultType evaluate_telemetry(
        const TelemetrySnapshot& snap, 
        const std::optional<TelemetrySnapshot>& prev) noexcept 
    {
        FaultType faults = FaultType::None;

        for (size_t ch = 0; ch < MaxChannels; ++ch) {
            if (snap.supply_current_ma[ch] > safety_.max_allowed_current_ma[ch]) {
                faults = faults | FaultType::Overcurrent;
            }
            if (snap.supply_voltage_v[ch] < safety_.min_allowed_voltage_v[ch] ||
                snap.supply_voltage_v[ch] > safety_.max_allowed_voltage_v[ch]) {
                faults = faults | FaultType::VoltageSag;
            }
        }

        if (snap.dut_hotspot_temp_c > safety_.max_dut_temp_c) {
            faults = faults | FaultType::ThermalRunaway;
        }

        if (prev.has_value() && snap.timestamp > prev->timestamp) {
            const auto dt_sec = std::chrono::duration<float>(snap.timestamp - prev->timestamp).count();
            const float dt_temp = std::abs(snap.dut_hotspot_temp_c - prev->dut_hotspot_temp_c);
            if ((dt_temp / dt_sec) > safety_.max_temp_slew_c_per_sec) {
                faults = faults | FaultType::ThermalRunaway;
            }
        }

        if (snap.vibration_g_rms > safety_.max_vibration_g_rms) {
            faults = faults | FaultType::VibrationOverload;
        }

        if (!snap.comm_alive) {
            consecutive_comm_failures_++;
            if (consecutive_comm_failures_ >= safety_.max_consecutive_comm_failures) {
                faults = faults | FaultType::CommTimeout;
            }
        } else {
            consecutive_comm_failures_ = 0;
        }

        if (snap.comm_crc_errors > 50) {
            faults = faults | FaultType::CrcErrorBurst;
        }

        return faults;
    }

    void tick(TelemetrySnapshot snap, std::chrono::milliseconds dt) noexcept {
        const auto prev = ring_.latest();
        snap.fault_mask = evaluate_telemetry(snap, prev);
        ring_.push(snap);

        if (has_fault(snap.fault_mask, FaultType::Overcurrent | FaultType::ThermalRunaway | FaultType::VibrationOverload)) {
            state_ = HaltState::EmergencyAbort;
            ring_.freeze();
            is_destructive_fault_ = true;
            udl_recorded_ = current_stress_level_;
            return;
        }

        if (current_step_idx_ >= scenario_.size()) {
            state_ = HaltState::Complete;
            return;
        }

        const auto& curr = scenario_[current_step_idx_];

        switch (state_) {
        case HaltState::Idle:
            current_step_idx_ = 0;
            state_timer_ = 0ms;
            state_ = HaltState::Ramp;
            break;

        case HaltState::Ramp: {
            const float ramp_per_sec = curr.ramp_rate_per_min / 60.0f;
            const float dt_sec = std::chrono::duration<float>(dt).count();
            const float delta = ramp_per_sec * dt_sec;

            if (current_stress_level_ < curr.target_value) {
                current_stress_level_ += delta;
                if (current_stress_level_ >= curr.target_value) {
                    current_stress_level_ = curr.target_value;
                    state_ = HaltState::Dwell;
                    state_timer_ = 0ms;
                }
            } else if (current_stress_level_ > curr.target_value) {
                current_stress_level_ -= delta;
                if (current_stress_level_ <= curr.target_value) {
                    current_stress_level_ = curr.target_value;
                    state_ = HaltState::Dwell;
                    state_timer_ = 0ms;
                }
            } else {
                state_ = HaltState::Dwell;
                state_timer_ = 0ms;
            }
            break;
        }

        case HaltState::Dwell:
            state_timer_ += dt;
            if (has_fault(snap.fault_mask, FaultType::CommTimeout | FaultType::CrcErrorBurst | FaultType::VoltageSag)) {
                state_ = HaltState::RecoveryCheck;
                state_timer_ = 0ms;
                if (curr.type == StressType::TemperatureHot || curr.type == StressType::VibrationRandom) {
                    uol_recorded_ = current_stress_level_;
                } else {
                    lol_recorded_ = current_stress_level_;
                }
            } else if (state_timer_ >= curr.dwell_time) {
                current_step_idx_++;
                state_ = HaltState::Ramp;
                state_timer_ = 0ms;
            }
            break;

        case HaltState::RecoveryCheck:
            state_timer_ += dt;
            if (snap.comm_alive && !has_fault(snap.fault_mask, FaultType::VoltageSag)) {
                current_step_idx_++;
                state_ = HaltState::Ramp;
                state_timer_ = 0ms;
            } else if (state_timer_ >= 5000ms) {
                is_destructive_fault_ = true;
                if (curr.type == StressType::TemperatureHot || curr.type == StressType::VibrationRandom) {
                    udl_recorded_ = current_stress_level_;
                } else {
                    ldl_recorded_ = current_stress_level_;
                }
                state_ = HaltState::EmergencyAbort;
                ring_.freeze();
            }
            break;

        case HaltState::EmergencyAbort:
        case HaltState::Complete:
            break;
        }
    }

    [[nodiscard]] HaltState state() const noexcept { return state_; }
    [[nodiscard]] float current_stress() const noexcept { return current_stress_level_; }
    [[nodiscard]] float lol() const noexcept { return lol_recorded_; }
    [[nodiscard]] float uol() const noexcept { return uol_recorded_; }
    [[nodiscard]] float ldl() const noexcept { return ldl_recorded_; }
    [[nodiscard]] float udl() const noexcept { return udl_recorded_; }

private:
    SafetyThresholds safety_;
    std::vector<StepConfig> scenario_;
    size_t current_step_idx_{0};
    HaltState state_{HaltState::Idle};
    
    TelemetryRingBuffer ring_{};
    float current_stress_level_{25.0f};
    std::chrono::milliseconds state_timer_{0ms};
    uint32_t consecutive_comm_failures_{0};

    float lol_recorded_{0.0f};
    float uol_recorded_{0.0f};
    float ldl_recorded_{0.0f};
    float udl_recorded_{0.0f};
    bool is_destructive_fault_{false};
};
