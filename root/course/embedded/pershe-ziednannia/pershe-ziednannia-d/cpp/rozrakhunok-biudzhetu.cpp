// Конфігурація частоти ATTITUDE на 20 Гц (інтервал 50 000 мкс) через COMMAND_LONG
void configureAttitudeStream(uint8_t gcs_sysid, uint8_t gcs_compid,
                             uint8_t target_sys, uint8_t target_comp) {
    mavlink_message_t msg;
    mavlink_msg_command_long_pack(
        gcs_sysid, gcs_compid, &msg,
        target_sys, target_comp,
        MAV_CMD_SET_MESSAGE_INTERVAL,
        0,                               // confirmation (номер спроби)
        30.0f,                           // param1: Message ID (30 = ATTITUDE)
        50000.0f,                        // param2: Інтервал 50 000 мкс = 20 Гц
        0.0f, 0.0f, 0.0f, 0.0f, 0.0f     // param3..param7: не використовуються
    );
    // Відправка msg у порт...
}
