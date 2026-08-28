// Зліт на висоту alt_m над точкою озброєння. Координати зльоту зазвичай
// лишають нульовими — апарат піднімається вертикально з місця, де стоїть.
// param1 у TAKEOFF — мінімальний кут тангажу (для літаків); для коптера 0.
static mavlink_mission_item_int_t make_takeoff(uint16_t seq, float alt_m) {
    mavlink_mission_item_int_t it = make_nav_item(seq, MAV_CMD_NAV_TAKEOFF, 0.0, 0.0, alt_m);
    it.param1 = 0.0f;   // мін. кут тангажу, град (коптеру байдуже)
    return it;
}

// Точка маршруту. param1 — час зависання, с (0 = проходь наскрізь);
// param2 — радіус прийняття, м (0 = взяти системний WPNAV_RADIUS).
static mavlink_mission_item_int_t make_waypoint(uint16_t seq,
        double lat_deg, double lon_deg, float alt_m,
        float hold_s = 0.0f, float accept_radius_m = 0.0f) {
    mavlink_mission_item_int_t it = make_nav_item(seq, MAV_CMD_NAV_WAYPOINT,
                                                  lat_deg, lon_deg, alt_m);
    it.param1 = hold_s;            // час зависання в точці, с
    it.param2 = accept_radius_m;   // радіус прийняття, м (0 → системний)
    return it;
}

// Повернення додому. RTL координат не потребує — «домівка» апарату відома;
// тож тут і x/y/z лишаються нулями, і параметри не використовуються.
static mavlink_mission_item_int_t make_rtl(uint16_t seq) {
    return make_nav_item(seq, MAV_CMD_NAV_RETURN_TO_LAUNCH, 0.0, 0.0, 0.0f);
}
