// Одна відправка кадру ARM/DISARM. confirmation = номер спроби.
static void send_arm(uint8_t confirmation, bool arm) {
    mavlink_message_t m;
    mavlink_msg_command_long_pack(
        MY_SYSID, MY_COMPID, &m,
        TARGET_SYS, TARGET_COMP,          // адреса апарата з HEARTBEAT
        MAV_CMD_COMPONENT_ARM_DISARM,     // command
        confirmation,                     // лічильник повторів ДЛЯ АПАРАТА
        arm ? 1.0f : 0.0f,                // param1: 1 → ARM, 0 → DISARM
        0,0,0,0,0,0);                     // param2..7 не потрібні
    uint8_t buf[MAVLINK_MAX_PACKET_LEN];
    serial_write(buf, mavlink_msg_to_send_buffer(buf, &m));
}

// Повертає код MAV_RESULT, або -1, якщо апарат промовчав усі спроби.
int arm_vehicle(bool arm) {
    const uint8_t  MAX_TRIES = 5;
    for (uint8_t attempt = 0; attempt < MAX_TRIES; ++attempt) {
        send_arm(attempt, arm);                 // спроба № attempt
        uint32_t deadline = millis() + 1500;    // таймаут на цю спробу
        while ((int32_t)(deadline - millis()) > 0) {
            mavlink_command_ack_t ack;
            // poll_command_ack() читає лінк і віддає true ЛИШЕ для ACK,
            // у якого ack.command == потрібний → чужий ACK не привласнимо.
            if (poll_command_ack(MAV_CMD_COMPONENT_ARM_DISARM, &ack)) {
                if (ack.result == MAV_RESULT_IN_PROGRESS) {
                    deadline = millis() + 5000; // довга дія: відсунути, чекати
                    continue;                   // це НЕ кінцева відповідь
                }
                return ack.result;              // остаточний код — віддати нагору
            }
            // важливо: тут-таки крутимо приймання решти телеметрії (див. нижче)
        }
        // таймаут: наступна ітерація перешле ARM з confirmation = attempt+1
    }
    return -1;   // апарат мовчить — лінк мертвий
}

// Виклик стає однорядковим, а всі коди розібрані за змістом:
int r = arm_vehicle(true);
if      (r == MAV_RESULT_ACCEPTED)              { /* мотори озброєно */ }
else if (r == MAV_RESULT_TEMPORARILY_REJECTED)  { /* зайнятий — спробувати згодом */ }
else if (r == MAV_RESULT_DENIED)                { /* не пройдено передпольотні перевірки */ }
else if (r == -1)                               { /* зв'язку нема — у безпечний стан */ }
