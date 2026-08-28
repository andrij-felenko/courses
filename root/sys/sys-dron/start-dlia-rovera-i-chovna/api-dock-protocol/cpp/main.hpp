#include <cstdint>
#include <array>
#include <span>

namespace autonomy::dock_protocol {

// Параметри команди MAVLink: MAV_CMD_DO_DOCK_EXIT (ID 42100)
struct DockExitCommand {
    float exit_direction_deg{0.0f};  // Param 1: Азимут виходу (0..360 deg)
    float clear_distance_m{1.8f};    // Param 2: Дистанція виходу у вільну зону (м)
    float max_exit_speed_mps{0.12f}; // Param 3: Максимальна швидкість реверсу (м/с)
    float burst_thrust_pct{75.0f};   // Param 4: Імпульс тяги відчалювання (%)
    float timeout_sec{15.0f};        // Param 5: Максимальний таймаут процедури (с)
    uint8_t flags{0x00};             // Param 6: Прапорці конфігурації
    uint8_t target_system_id{1};     // Param 7: ID дока
};

// Декодований стан зарядної док-станції
struct DockStatus {
    uint8_t state{0};
    uint16_t voltage_mv{0};
    int16_t current_ma{0};
    bool relay_closed{false};
    bool pilot_present{false};
    bool mech_locked{false};
    bool fault_overcurrent{false};
    bool fault_relay_weld{false};

    static constexpr DockStatus from_can_payload(std::span<const uint8_t, 8> payload) noexcept {
        DockStatus s{};
        s.state = payload[0];
        s.voltage_mv = static_cast<uint16_t>(payload[1] | (payload[2] << 8));
        s.current_ma = static_cast<int16_t>(payload[3] | (payload[4] << 8));
        s.relay_closed = (payload[5] & 0x01) != 0;
        s.pilot_present = (payload[5] & 0x02) != 0;
        s.mech_locked = (payload[5] & 0x04) != 0;
        s.fault_overcurrent = (payload[6] & 0x01) != 0;
        s.fault_relay_weld = (payload[6] & 0x08) != 0;
        return s;
    }
};

} // namespace autonomy::dock_protocol
