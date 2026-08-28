void onError(const mavlink_message_t &msg)
{
    mavlink_response_event_error_t err;
    mavlink_msg_response_event_error_decode(&msg, &err);

    if (err.target_system != _our_sysid || err.target_component != _our_compid) {
        return;                         // відповідь не нам
    }
    if (compare(static_cast<uint16_t>(_latest + 1), err.sequence) != Cmp::equal) {
        return;                         // відповідь не на той номер, якого ми чекаємо
    }

    const uint16_t num_lost =
        static_cast<uint16_t>(err.sequence_oldest_available - _latest - 1);
    _lost_total += num_lost;
    _cb.lost(num_lost);

    _latest = static_cast<uint16_t>(err.sequence_oldest_available - 1);
    request(static_cast<uint16_t>(_latest + 1));
}
