// Крок 1: попросити борт вивантажити його ПОТОЧНУ місію (не ту, що ми «мали б» залити).
mavlink_msg_mission_request_list_send(chan, tgt_sys, tgt_comp, MAV_MISSION_TYPE_MISSION);
uint16_t count = wait_mission_count();      // борт відповість MISSION_COUNT

// Крок 2: по одному пункту, з таймаутом і обмеженим числом повторів.
for (uint16_t seq = 0; seq < count; seq++) {
    mavlink_mission_item_int_t it;
    int tries = 0;
    do {
        request_item_int(seq);              // MISSION_REQUEST_INT(seq)
    } while (!recv_item(&it, seq, /*timeout_ms=*/250) && ++tries < 5);
    if (tries >= 5) { abort_readback(); return; }   // здався — не звіряємо частковий список

    // Крок 3: звірити з тим, що ЗАДУМАНО, декодувавши цілі назад у градуси.
    if (it.command == MAV_CMD_NAV_WAYPOINT) {
        double lat = it.x * 1e-7;           // 10⁻⁷ градуса → градуси
        double lon = it.y * 1e-7;
        float  alt = it.z;                  // метри — але В ЯКІЙ системі? див. it.frame нижче
        printf("#%u  %.7f, %.7f  alt=%.1f  frame=%u\n", seq, lat, lon, alt, it.frame);
    }
}
