// Зібрати й відіслати команду «озброїти мотори».
// confirmation=0 для першої спроби; param1=1 → ARM (0 → DISARM).
mavlink_message_t msg;
mavlink_msg_command_long_pack(
    my_sysid, my_compid, &msg,
    target_sys, target_comp,            // кому: SYS/COMP апарата з HEARTBEAT
    MAV_CMD_COMPONENT_ARM_DISARM,       // command (ID із набору MAV_CMD)
    0,                                  // confirmation
    1.0f,                               // param1 = 1 → armed
    0,0,0,0,0,0);                       // param2..7 не використовуються
uint8_t buf[MAVLINK_MAX_PACKET_LEN];
int n = mavlink_msg_to_send_buffer(buf, &msg);
serial_write(buf, n);

// Дочекатися COMMAND_ACK саме на цю команду й прочитати результат.
mavlink_command_ack_t ack;
if (wait_command_ack(MAV_CMD_COMPONENT_ARM_DISARM, &ack, /*timeout_ms=*/1000)) {
    if (ack.result == MAV_RESULT_ACCEPTED)
        printf("armed\n");                       // мотори озброєно
    else
        printf("arm denied: %u\n", ack.result);  // напр. DENIED — не пройшли перевірки
} else {
    // ACK не прийшов: збільшуємо confirmation і шлемо ту саму команду знову
    resend_with_confirmation(MAV_CMD_COMPONENT_ARM_DISARM, /*confirmation=*/1);
}
