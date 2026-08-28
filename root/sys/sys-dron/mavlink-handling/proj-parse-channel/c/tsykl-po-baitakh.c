static void rx_feed(rx_t *rx, const uint8_t *chunk, size_t n)
{
    for (size_t i = 0; i < n; ++i) {
        mavlink_message_t msg;
        mavlink_status_t  st;

        const uint8_t framing = mavlink_frame_char(rx->chan, chunk[i], &msg, &st);
        rx->verdict[framing]++;

        switch (framing) {
        case MAVLINK_FRAMING_OK:
            rx->whole++;
            rx_account(rx, &msg);
            break;

        case MAVLINK_FRAMING_BAD_CRC:
            /* msgid уже розібрано, тож можна відрізнити шум від чужого діалекту */
            if (mavlink_get_msg_entry(msg.msgid) == NULL) {
                rx->alien++;
            }
            rx_resync(rx, chunk[i]);
            break;

        case MAVLINK_FRAMING_BAD_SIGNATURE:
            rx_resync(rx, chunk[i]);
            break;

        default:                       /* MAVLINK_FRAMING_INCOMPLETE */
            break;
        }
    }
}
