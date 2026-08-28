/* Бік прошивки: пакування кадру бібліотекою MAVLink C.
   Перші два аргументи — ХТО шле, наступні два — КОМУ. */
mavlink_message_t msg;

mavlink_msg_command_long_pack(
    255,                                /* sysid            — наш номер системи   */
    MAV_COMP_ID_MISSIONPLANNER,         /* compid           — наш номер компонента = 190 */
    &msg,
    1,                                  /* target_system    — апарат номер 1      */
    MAV_COMP_ID_AUTOPILOT1,             /* target_component — його автопілот = 1  */
    MAV_CMD_COMPONENT_ARM_DISARM,       /* команда 400                            */
    0,                                  /* confirmation                           */
    1.0f,                               /* param1: 1 — зброїти, 0 — розброїти     */
    0, 0, 0, 0, 0, 0);

uint8_t buf[MAVLINK_MAX_PACKET_LEN];
const uint16_t len = mavlink_msg_to_send_buffer(buf, &msg);
port_write(buf, len);
