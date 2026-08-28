// Псевдо-C для ясності послідовності; на практиці — pymavlink на землі.
// Крок 1: попросити борт вивантажити його поточну місію.
mavlink_msg_mission_request_list_send(chan, target_sys, target_comp,
                                      MAV_MISSION_TYPE_MISSION);

// Крок 2: борт відповість MISSION_COUNT; далі просимо кожен пункт по seq.
for (uint16_t seq = 0; seq < count; seq++) {
    request_mission_item(seq);                 // MISSION_REQUEST_INT(seq)
    mavlink_mission_item_int_t it = wait_item(seq);

    // Крок 3: звірити з тим, що ЗАДУМАНО (не з тим, що «мали б надіслати»).
    if (it.command == MAV_CMD_NAV_WAYPOINT) {
        double lat = it.x * 1e-7;              // 10⁻⁷ градуса → градуси
        double lon = it.y * 1e-7;
        float  alt = it.z;                     // метри над точкою старту
        printf("#%u  %.7f, %.7f  alt=%.1f m\n", seq, lat, lon, alt);
    }
}
