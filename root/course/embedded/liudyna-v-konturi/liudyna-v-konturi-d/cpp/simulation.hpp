#pragma once

#include <iosfwd>
#include <string_view>

#include "vehicle.hpp"

namespace hitl {

struct Scenario {
    std::string_view name;
    ControlMode mode{ControlMode::Rate};
    float link_delay{0.0f};   // «скло-до-скла» плюс «стік-до-мотора», с
    float jitter{0.0f};       // половина розкиду затримки відеотракту, с
    bool jitter_buffer{false};
    bool pio_suppression{false};  // бортове пригнічення розкачки
    bool lead_ahead_hud{false};   // предиктивний маркер на екрані оператора
    float expo{0.0f};             // крива стіка на пульті
};

struct Report {
    float pilot_gain{0.0f};
    float pilot_lead{0.0f};
    float pure_delay{0.0f};       // сума ЧИСТИХ затримок контуру, с
    float phase_margin0_deg{0.0f};
    float phase_margin_deg{0.0f};
    float link_budget{0.0f};      // скільки лагу канал ще витримає, с
    float max_angle_deg{0.0f};
    float osc_freq_hz{0.0f};
    float osc_amp_deg{0.0f};
    float osc_growth{1.0f};
    float stick_gyro_corr{0.0f};
    float saturation{0.0f};
    int video_freezes{0};
    bool pio{false};
};

// Проганяє один сценарій, друкуючи хід симуляції у trace.
[[nodiscard]] Report Run(const Scenario& sc, std::ostream& trace);

}  // namespace hitl
