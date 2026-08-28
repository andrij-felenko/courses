static void rx_resync(rx_t *rx, uint8_t c)
{
    mavlink_status_t  *st    = mavlink_get_channel_status(rx->chan);
    mavlink_message_t *rxmsg = mavlink_get_channel_buffer(rx->chan);

    st->msg_received = MAVLINK_FRAMING_INCOMPLETE;
    st->parse_state  = MAVLINK_PARSE_STATE_IDLE;

    /* байт, на якому кадр завалився, сам може бути стартом наступного */
    if (c == MAVLINK_STX || c == MAVLINK_STX_MAVLINK1) {
        st->parse_state = MAVLINK_PARSE_STATE_GOT_STX;
        rxmsg->magic    = c;
        rxmsg->len      = 0;

        if (c == MAVLINK_STX_MAVLINK1) {
            st->flags |=  MAVLINK_STATUS_FLAG_IN_MAVLINK1;
        } else {
            st->flags &= ~MAVLINK_STATUS_FLAG_IN_MAVLINK1;
        }
        mavlink_start_checksum(rxmsg);
    }
}
