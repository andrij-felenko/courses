void onCurrent(const mavlink_message_t &msg)
{
    mavlink_current_event_sequence_t cur;
    mavlink_msg_current_event_sequence_decode(&msg, &cur);

    if (cur.flags & MAV_EVENT_CURRENT_SEQUENCE_FLAGS_RESET) {
        _has_sequence = false;
        ++_reboots;
    }
    if (!_has_sequence) {
        _has_sequence = true;
        _latest = cur.sequence;     // не sequence − 1: цієї події ми не бачили й не побачимо
    }

    if (compare(_latest, cur.sequence) == Cmp::newer) {
        request(static_cast<uint16_t>(_latest + 1));
    }

    _has_current    = true;
    _latest_current = cur.sequence;
}
