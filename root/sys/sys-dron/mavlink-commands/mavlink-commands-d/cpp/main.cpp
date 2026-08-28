// MAV_CMD_NAV_TAKEOFF — команда взльоту; висота йде в param7.
mavlink_command_long_t cmd = {0};      // обнуляємо всі поля
cmd.target_system    = 1;              // якому апарату
cmd.target_component = 1;              // автопілоту цього апарата
cmd.command          = MAV_CMD_NAV_TAKEOFF;
cmd.confirmation     = 0;              // перша відправка
cmd.param7           = 10.0f;          // цільова висота, метри

mavlink_message_t msg;
mavlink_msg_command_long_encode(255, 190, &msg, &cmd);  // 255/190 — адреса станції

uint8_t buf[MAVLINK_MAX_PACKET_LEN];
int len = mavlink_msg_to_send_buffer(buf, &msg);        // готові байти кадру
serial_write(buf, len);                                 // у радіоканал
// далі — чекаємо COMMAND_ACK і дивимося cmd_ack.result
