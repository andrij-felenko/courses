static uint16_t frame_heartbeat(uint8_t *out, uint8_t chan, uint8_t sysid, uint8_t compid)
{
    mavlink_message_t msg;
    mavlink_msg_heartbeat_pack_chan(sysid, compid, chan, &msg,
                                    MAV_TYPE_QUADROTOR, MAV_AUTOPILOT_PX4,
                                    MAV_MODE_FLAG_SAFETY_ARMED, 0, MAV_STATE_ACTIVE);
    return mavlink_msg_to_send_buffer(out, &msg);
}

/* кадр із номером повідомлення, якого немає в жодному діалекті */
static size_t frame_alien(uint8_t *out)
{
    out[0] = MAVLINK_STX;   /* 0xFD                       */
    out[1] = 4;             /* довжина навантаження       */
    out[2] = 0;             /* прапорці несумісності      */
    out[3] = 0;             /* прапорці сумісності        */
    out[4] = 7;             /* номер послідовності        */
    out[5] = 1;             /* система                    */
    out[6] = 42;            /* компонент                  */
    out[7] = 0xF0;          /* msgid, молодший байт       */
    out[8] = 0xFF;
    out[9] = 0xFF;          /* msgid = 0xFFFFF0           */
    out[10] = 1; out[11] = 2; out[12] = 3; out[13] = 4;
    out[14] = 0x00;         /* суми, якої розбирач однаково не перевірить */
    out[15] = 0x00;
    return 16;
}
