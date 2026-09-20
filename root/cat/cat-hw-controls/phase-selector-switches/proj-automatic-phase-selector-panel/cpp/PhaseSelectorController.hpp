#pragma once

#include <cstdint>
#include <array>
#include <optional>
#include <iostream>

namespace hw_controls {

enum class PhaseId : uint8_t {
    None = 0,
    L1   = 1,
    L2   = 2,
    L3   = 3
};

enum class FsmState : uint8_t {
    Init,
    Monitoring,
    BreakBeforeMake, // Dead-time безнапругової паузи
    ReturnDelay,     // Затримка повернення на пріоритетну L1
    AllPhasesFault
};

struct VoltageThresholds {
    float u_min{195.0f};       // Нижній поріг напруги (V)
    float u_max{253.0f};       // Верхній поріг напруги (V)
    float u_hysteresis{5.0f};   // Гістерезис відновлення (V)
};

struct TimerConfig {
    uint32_t t_delay_ms{100};   // Затримка спрацьовування при просіданні
    uint32_t t_dead_ms{50};     // Безнапругова пауза Break-Before-Make
    uint32_t t_return_ms{3000}; // Затримка повернення на L1
};

struct PhaseMeasurements {
    float u_l1{0.0f};
    float u_l2{0.0f};
    float u_l3{0.0f};
};

class PhaseSelectorController {
public:
    explicit PhaseSelectorController(const VoltageThresholds& thresholds = {},
                                     const TimerConfig& timers = {});

    void update(const PhaseMeasurements& measurements, uint32_t dt_ms);

    [[nodiscard]] PhaseId getActivePhase() const noexcept { return active_phase_; }
    [[nodiscard]] PhaseId getTargetPhase() const noexcept { return target_phase_; }
    [[nodiscard]] FsmState getState() const noexcept { return state_; }

    [[nodiscard]] bool isPhaseValid(PhaseId phase, float voltage) const noexcept;

private:
    [[nodiscard]] PhaseId selectBestPhase(const PhaseMeasurements& m) const noexcept;

    VoltageThresholds thresholds_;
    TimerConfig timers_;

    FsmState state_{FsmState::Init};
    PhaseId active_phase_{PhaseId::None};
    PhaseId target_phase_{PhaseId::None};
    uint32_t state_timer_ms_{0};
    uint32_t fault_timer_ms_{0};
};

} // namespace hw_controls
