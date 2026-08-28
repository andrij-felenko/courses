#include <stdint.h>
#include <stdbool.h>

// Параметри команди MAVLink: MAV_CMD_DO_DOCK_EXIT (ID 42100)
// Відправляється автопілотом до контролера дока або диспетчера
typedef struct {
    float exit_direction_deg; // Param 1: Кут напрямку виходу з дока (0..360 deg)
    float clear_distance_m;   // Param 2: Відстань виходу у безпечну зону (метри)
    float max_exit_speed_mps; // Param 3: Максимальна швидкість реверсу (м/с)
    float burst_thrust_pct;   // Param 4: Відсоток імпульсної тяги відчалювання (0..100%)
    float timeout_sec;        // Param 5: Максимальний таймаут виконання процедури (секунди)
    float flags;              // Param 6: Бітова маска (0x01: Force Unlatch, 0x02: Skip Compass)
    float target_system_id;   // Param 7: ID док-станції
} mavlink_cmd_dock_exit_t;

// Декодування вхідного бінарного фрейму CAN стану док-станції
typedef struct {
    uint8_t dock_state;
    uint16_t voltage_mv;
    int16_t current_ma;
    bool relay_closed;
    bool pilot_present;
    bool mech_locked;
    bool fault_overcurrent;
    bool fault_relay_weld;
} dock_decoded_status_t;

static inline void decode_dock_can_frame(const uint8_t data[8], dock_decoded_status_t *out) {
    out->dock_state = data[0];
    out->voltage_mv = (uint16_t)(data[1] | (data[2] << 8));
    out->current_ma = (int16_t)(data[3] | (data[4] << 8));
    out->relay_closed = (data[5] & 0x01) != 0;
    out->pilot_present = (data[5] & 0x02) != 0;
    out->mech_locked = (data[5] & 0x04) != 0;
    out->fault_overcurrent = (data[6] & 0x01) != 0;
    out->fault_relay_weld = (data[6] & 0x08) != 0;
}
