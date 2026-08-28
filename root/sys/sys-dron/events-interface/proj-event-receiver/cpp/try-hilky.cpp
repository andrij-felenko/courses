void onEvent(const mavlink_message_t &msg)
{
    mavlink_event_t ev;
    mavlink_msg_event_decode(&msg, &ev);

    checkReboot(ev.event_time_boot_ms);

    if (!_has_sequence) {               // перша подія від цього компонента
        _has_sequence = true;
        _latest = static_cast<uint16_t>(ev.sequence - 1);
    }

    switch (compare(static_cast<uint16_t>(_latest + 1), ev.sequence)) {
    case Cmp::older:                    // дублікат: інваріант його вже покриває
        RX_TRACE("  дублікат seq=%u\n", unsigned(ev.sequence));
        ++_duplicates;
        return;                         // таймер НЕ чіпаємо
    case Cmp::newer:                    // між _latest і ev.sequence зяє діра
        RX_TRACE("  пропуск: чекали %u, прийшла %u\n",
                 unsigned(uint16_t(_latest + 1)), unsigned(ev.sequence));
        request(static_cast<uint16_t>(_latest + 1));
        return;                         // саму подію викидаємо
    case Cmp::equal:
        break;
    }

    _latest       = ev.sequence;
    _last_boot_ms = ev.event_time_boot_ms;
    _cb.timer(-1);                      // очікуване прийшло — таймер більше не потрібен

    if (_has_current && compare(_latest, _latest_current) == Cmp::newer) {
        request(static_cast<uint16_t>(_latest + 1));   // борт попереду — просимо далі
    }

    if (ev.destination_system != _our_sysid && ev.destination_system != 0) {
        return;
    }
    if (ev.destination_component != _our_compid &&
        ev.destination_component != MAV_COMP_ID_ALL) {
        return;
    }

    _cb.deliver(ev);
}
