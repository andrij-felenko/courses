#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

// Визначення структур MAVLink
typedef struct {
    uint32_t custom_mode;
    uint8_t  type;
    uint8_t  autopilot;
    uint8_t  base_mode;
    uint8_t  system_status;
    uint8_t  mavlink_version;
} mavlink_heartbeat_t;

#define MAV_MODE_FLAG_SAFETY_ARMED        128  // 0x80
#define MAV_MODE_FLAG_CUSTOM_MODE_ENABLED 1    // 0x01
#define MAV_STATE_ACTIVE                  4
#define MAV_TYPE_QUADROTOR                2
#define MAV_AUTOPILOT_PX4                 12

void process_heartbeat(uint8_t sysid, uint8_t compid, const mavlink_heartbeat_t* hb) {
    bool is_armed = (hb->base_mode & MAV_MODE_FLAG_SAFETY_ARMED) != 0;
    bool is_custom = (hb->base_mode & MAV_MODE_FLAG_CUSTOM_MODE_ENABLED) != 0;

    printf("Отримано HEARTBEAT від [SYS %u, COMP %u]:\n", sysid, compid);
    printf("  Тип апарата: %s (код %u)\n", 
           (hb->type == MAV_TYPE_QUADROTOR) ? "Квадрокоптер" : "Інший", hb->type);
    printf("  Прошивка:    %s (код %u)\n", 
           (hb->autopilot == MAV_AUTOPILOT_PX4) ? "PX4 Autopilot" : "Інша", hb->autopilot);
    printf("  Стан моторів: %s\n", is_armed ? "ARMED (НЕБЕЗПЕЧНО)" : "DISARMED (ВИМКНЕНО)");
    printf("  Стан системи: %s (код %u)\n", 
           (hb->system_status == MAV_STATE_ACTIVE) ? "ACTIVE (Політ)" : "Очікування", hb->system_status);

    if (is_custom && hb->autopilot == MAV_AUTOPILOT_PX4) {
        // У PX4 старші 16 біт custom_mode зберігають головний режим
        uint8_t main_mode = (hb->custom_mode >> 16) & 0xFF;
        printf("  Головний режим PX4: 0x%02X (POSCTL утримання позиції)\n", main_mode);
    }
}
