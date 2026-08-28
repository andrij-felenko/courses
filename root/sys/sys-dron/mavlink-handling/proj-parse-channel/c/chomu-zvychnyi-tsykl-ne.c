MAVLINK_HELPER uint8_t mavlink_parse_char(uint8_t chan, uint8_t c,
                                          mavlink_message_t* r_message,
                                          mavlink_status_t* r_mavlink_status)
{
    uint8_t msg_received = mavlink_frame_char(chan, c, r_message, r_mavlink_status);
    if (msg_received == MAVLINK_FRAMING_BAD_CRC ||
        msg_received == MAVLINK_FRAMING_BAD_SIGNATURE) {
        // we got a bad CRC. Treat as a parse failure
        mavlink_message_t* rxmsg = mavlink_get_channel_buffer(chan);
        mavlink_status_t* status = mavlink_get_channel_status(chan);
        _mav_parse_error(status);
        status->msg_received = MAVLINK_FRAMING_INCOMPLETE;
        status->parse_state = MAVLINK_PARSE_STATE_IDLE;
        if (c == MAVLINK_STX)
        {
            status->parse_state = MAVLINK_PARSE_STATE_GOT_STX;
            rxmsg->len = 0;
            mavlink_start_checksum(rxmsg);
        }
        return 0;
    }
    return msg_received;
}
