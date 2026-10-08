#include <stdint.h>
#include <stdbool.h>

// Адреси регістрів CiA 402
#define REG_CONTROLWORD        0x6040
#define REG_OP_MODE            0x6060
#define REG_TARGET_POSITION    0x607A
#define REG_PROFILE_VELOCITY   0x6081

// Прапори Controlword для переходу в стан Operation Enabled
#define CTRL_SHUTDOWN          0x0006 // Ready to Switch On
#define CTRL_SWITCH_ON         0x0007 // Switched On
#define CTRL_ENABLE_OP         0x000F // Operation Enabled
#define CTRL_NEW_SETPOINT      (1 << 4)

typedef struct {
    uint16_t controlword;
    int8_t op_mode;
    int32_t target_position;
    uint32_t profile_velocity;
} ServoCommandState;

// Послідовність команд для запуску руху в режимі Profile Position
void configure_position_movement(ServoCommandState *cmd, int32_t target_counts, uint32_t max_speed) {
    // 1. Встановлюємо режим Profile Position (Код 1)
    cmd->op_mode = 1;
    cmd->profile_velocity = max_speed;
    cmd->target_position = target_counts;
    
    // 2. Послідовне увімкнення сипового каскаду (автомат станів CiA 402)
    cmd->controlword = CTRL_SHUTDOWN;
    cmd->controlword = CTRL_SWITCH_ON;
    cmd->controlword = CTRL_ENABLE_OP;
    
    // 3. Зведення фронту New Setpoint для застосування нової позиції
    cmd->controlword |= CTRL_NEW_SETPOINT;
}
