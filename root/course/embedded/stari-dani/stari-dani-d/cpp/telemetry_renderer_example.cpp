/* telemetry_renderer_example.cpp — Приклад використання модуля рендерингу віджетів на C++ */
#include "telemetry_age_tracker.hpp"
#include <iostream>

struct FlightInstruments {
    telemetry::TelemetrySlot<float> altitude_m{500, 2000};
    telemetry::TelemetrySlot<float> airspeed_mps{300, 1500};
    telemetry::TelemetrySlot<uint8_t> battery_pct{2000, 6000};
};

void render_gui_frame(const FlightInstruments& instruments, uint32_t now_ms) {
    const auto alt_state = instruments.altitude_m.get_visual_state(now_ms);
    const float* alt_val = instruments.altitude_m.get_valid_value(now_ms);

    std::cout << "--- Індикатор висоти ---\n";
    std::cout << "Прозорість (Alpha): " << alt_state.alpha_opacity << "\n";
    
    if (alt_state.cross_out_required) {
        std::cout << "СТАН: [ ✖ ЧЕРВОНИЙ ХРЕСТ: ДАНІ НЕ ДІЙСНІ ] -> ALT: - - -\n";
    } else if (alt_state.show_age_badge) {
        std::cout << "СТАН: [ ЖОВТА РАМКА (" << alt_state.age_text << ") ] -> ALT: " 
                  << (alt_val ? *alt_val : 0.0f) << " м\n";
    } else {
        std::cout << "СТАН: [ СВІЖО (100% контраст) ] -> ALT: " 
                  << (alt_val ? *alt_val : 0.0f) << " м\n";
    }
}
