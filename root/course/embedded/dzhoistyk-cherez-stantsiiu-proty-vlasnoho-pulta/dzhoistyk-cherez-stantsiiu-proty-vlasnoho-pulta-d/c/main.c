// Бортовий захист від застигання осей MAVLink MANUAL_CONTROL
#include <stdint.h>
#include <stdbool.h>

typedef struct {
    int16_t roll;
    int16_t pitch;
    int16_t throttle;
    int16_t yaw;
} AxisCommands;

void process_manual_control_timeout(AxisCommands *cmd, uint32_t last_packet_ms, uint32_t now_ms) {
    uint32_t dt = now_ms - last_packet_ms;
    
    if (dt > 250 && dt <= 1000) {
        // М'яка нейтралізація: крен і тангаж у нуль
        cmd->roll = 0;
        cmd->pitch = 0;
        cmd->yaw = 0;
        // Тягу тримаємо на рівні зависання (500)
        cmd->throttle = 500;
    } else if (dt > 1000) {
        // Повний Failsafe: аварійна посадка або повернення додому
        cmd->roll = 0;
        cmd->pitch = 0;
        cmd->yaw = 0;
        cmd->throttle = 0;
    }
}
