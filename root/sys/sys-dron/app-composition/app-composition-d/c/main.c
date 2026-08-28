const uint8_t chan = link->mavlinkChannel();

for (int i = 0; i < data.size(); i++) {
    mavlink_message_t message;
    mavlink_status_t  status;
    const uint8_t framing = mavlink_parse_char(chan, data[i], &message, &status);

    if (framing == MAVLINK_FRAMING_OK) {
        emit messageReceived(link, message);
    }
}
