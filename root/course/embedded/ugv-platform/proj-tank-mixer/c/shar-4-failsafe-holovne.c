// ── Failsafe: годинник свіжості радіоканалу ──
#define LINK_TIMEOUT_MS   100    // тиша довша за це → лінк мертвий, газ у нуль

static uint32_t last_rc_ms = 0;  // час останнього СВІЖОГО кадру з приймача

// Викликати ЩОРАЗУ, коли приймач приніс новий кадр каналів.
void rc_mark_fresh(uint32_t now_ms) {
    last_rc_ms = now_ms;
}

// true, якщо зв'язок живий (свіжий кадр був не давніше за таймаут).
// Віднімання беззнакових — навмисне: коректне навіть при переповненні millis().
static bool link_alive(uint32_t now_ms) {
    return (now_ms - last_rc_ms) < LINK_TIMEOUT_MS;
}
