void request(uint16_t sequence)
{
    mavlink_request_event_t req{};
    req.target_system    = _sysid;
    req.target_component = _compid;
    req.first_sequence   = sequence;
    req.last_sequence    = sequence;

    ++_requests;
    _cb.send_request(req);
    _cb.timer(100);      // не прийшло за 100 мс — попросимо ще раз
}

void onTimeout()
{
    RX_TRACE("  таймер: повторюємо запит\n");
    request(static_cast<uint16_t>(_latest + 1));
}
