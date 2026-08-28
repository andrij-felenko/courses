#define LINK_TIMEOUT_S 3.0   // тиша довша за це = лінію втрачено (≈3 пропущені heartbeat)

typedef struct {
    double last_heartbeat;   // < 0 = heartbeat ще НЕ приходив жодного разу
    bool   armed;            // презумпція: роззброєно, поки не почули інше
    double alt_m, lat, lon, batt_v;
    uint8_t target_system, target_component;
    bool   safe;
} LinkState;

static void link_state_init(LinkState *st) {
    memset(st, 0, sizeof *st);
    st->last_heartbeat = -1.0;   // сентинел «ще не чули»
}

// True лише якщо heartbeat приходив І не замовк довше за поріг.
static bool link_alive(const LinkState *st) {
    if (st->last_heartbeat < 0)                      // ще жодного heartbeat — лінія НЕ жива
        return false;
    return (now_monotonic() - st->last_heartbeat) < LINK_TIMEOUT_S;
}
