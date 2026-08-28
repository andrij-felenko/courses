case MAVLINK_PARSE_STATE_GOT_PAYLOAD: {
    const mavlink_msg_entry_t *e = mavlink_get_msg_entry(rxmsg->msgid);
    if (e == NULL) {
        // Message not found in CRC_EXTRA table.
        status->parse_state = MAVLINK_PARSE_STATE_GOT_BAD_CRC1;
        rxmsg->ck[0] = c;
    } else {
        …
    }
}
