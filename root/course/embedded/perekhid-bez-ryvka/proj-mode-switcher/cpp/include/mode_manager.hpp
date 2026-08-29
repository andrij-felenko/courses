#pragma once

#include <cstdint>
#include <string_view>

#include "bumpless_pid.hpp"

namespace fc {

enum class FlightMode : std::uint8_t { Manual = 0, AltHold, AutoMission };

// Підказка пілоту на екран пульта чи світлодіод.
enum class StickHint : std::uint8_t { None = 0, PushUp, PushDown, Matched };

struct VehicleState {      // те, що дала фузія сенсорів на цьому такті
    float altitude_m{0.0f};
    float climb_mps{0.0f};
    float heading_deg{0.0f};
};

struct PilotInput {        // те, що прийшло з пульта
    float throttle{0.0f};        // 0..1
    bool force_override{false};  // AUX2 — силове перехоплення
    bool valid{false};           // лінк живий
};

struct ModeOutput {
    float throttle{0.0f};
    std::uint16_t dshot_value{0};
    std::uint16_t dshot_packet{0};
    float heading_cmd_deg{0.0f};
    StickHint hint{StickHint::None};
};

class ModeManager {
public:
    static constexpr float kStickMatchWindow = 0.03f;   // ±3 % навколо тяги
    static constexpr float kYawRateMaxDps = 45.0f;      // темп розвороту на базу
    static constexpr float kHandoverTolerance = 0.005f;

    ModeManager(float home_alt_m, float home_bearing_deg) noexcept;

    // Повертає залишковий стрибок виходу або причину відмови.
    std::expected<float, HandoverError> request_mode(FlightMode mode,
                                                     const VehicleState& state) noexcept;

    void enter_failsafe(const VehicleState& state) noexcept;
    void clear_failsafe() noexcept;

    void set_armed(bool armed) noexcept { armed_ = armed; }
    void set_mission_target(float altitude_m) noexcept;

    ModeOutput step(const PilotInput& pilot, const VehicleState& state, float dt) noexcept;

    [[nodiscard]] FlightMode mode() const noexcept { return mode_; }
    [[nodiscard]] bool failsafe() const noexcept { return failsafe_; }
    [[nodiscard]] float held_output() const noexcept { return u_hold_; }
    [[nodiscard]] unsigned handover_warnings() const noexcept { return handover_warnings_; }
    [[nodiscard]] unsigned rejected_switches() const noexcept { return rejected_switches_; }
    [[nodiscard]] const BumplessPid& active_pid() const noexcept;

private:
    FlightMode mode_{FlightMode::Manual};
    BumplessPid alt_hold_;
    BumplessPid mission_;
    float last_out_{0.0f};

    bool stick_hold_{false};   // Stick Matching: тримаємо тягу самі
    float u_hold_{0.0f};

    bool failsafe_{false};
    bool armed_{false};

    float mission_alt_m_;
    float home_alt_m_;
    float home_bearing_deg_;
    float heading_cmd_deg_{0.0f};

    unsigned handover_warnings_{0};
    unsigned rejected_switches_{0};
};

[[nodiscard]] std::string_view to_string(FlightMode mode) noexcept;
[[nodiscard]] std::string_view to_string(StickHint hint) noexcept;

}  // namespace fc
