#include <mavlink.h>

void send_control_high_latency_command(uint8_t target_sys, uint8_t target_comp, bool enable) {
    mavlink_message_t msg;
    mavlink_command_long_t cmd = {0};

    cmd.target_system    = target_sys;
    cmd.target_component = target_comp;
    cmd.command          = MAV_CMD_CONTROL_HIGH_LATENCY; // Команда #2600
    cmd.confirmation     = 0;
    cmd.param1           = enable ? 1.0f : 0.0f;        // 1.0 = Увімкнути HLP, 0.0 = Вимкнути
    cmd.param2           = 0.0f;                         // Резерв
    cmd.param3           = 0.0f;
    cmd.param4           = 0.0f;
    cmd.param5           = 0.0f;
    cmd.param6           = 0.0f;
    cmd.param7           = 0.0f;

    mavlink_msg_command_long_encode(255, 190, &msg, &cmd);
    // Відправка пакета в активний канал зв'язку
}
