// Контекст локального автономного регулятора на C++20
#include <cstdint>
#include <optional>
#include <concepts>

namespace embedded::edge {

enum class NetworkMode : uint8_t {
    OnlineSynced,
    OfflineSovereign,
    ReconcilingDrain
};

struct SovereignNode {
    int16_t target_temp_x10{220};      // 22.0 °C
    int16_t hysteresis_x10{10};       // 1.0 °C
    bool    safety_alarm_active{false};
    bool    actuator_relay_state{false};
    uint32_t state_generation{1};

    // Обчислення керуючого впливу без блокувань та виділення пам'яті
    constexpr void step(int16_t current_temp_x10) noexcept {
        // 1. Захисний інваріант аварії
        if (current_temp_x10 > 500) {
            safety_alarm_active = true;
            actuator_relay_state = false;
            ++state_generation;
            return;
        }

        if (safety_alarm_active) {
            actuator_relay_state = false;
            return;
        }

        // 2. Гістерезисний регулятор
        const int16_t low_bound  = target_temp_x10 - hysteresis_x10;
        const int16_t high_bound = target_temp_x10 + hysteresis_x10;

        if (current_temp_x10 < low_bound && !actuator_relay_state) {
            actuator_relay_state = true;
            ++state_generation;
        } else if (current_temp_x10 > high_bound && actuator_relay_state) {
            actuator_relay_state = false;
            ++state_generation;
        }
    }
};

} // namespace embedded::edge
