typedef struct { double period, last; } RateLimiter;

static void rate_init(RateLimiter *r, double hz) {
    r->period = 1.0 / hz;
    r->last = 0.0;
}

// Пропускає дію не частіше, ніж раз на period секунд.
static bool rate_ready(RateLimiter *r) {
    double now = now_monotonic();
    if (now - r->last >= r->period) {
        r->last = now;
        return true;
    }
    return false;
}

// приклад: слати навігаційну уставку не частіше 5 разів на секунду
static RateLimiter setpoint_rate;   // rate_init(&setpoint_rate, 5.0) — при старті

static void maybe_send_setpoint(int fd, LinkState *st) {
    if (!link_alive(st)) return;              // мертва лінія — не шлемо нічого
    if (!rate_ready(&setpoint_rate)) return;  // ще рано — цей такт пропускаємо
    (void)fd;
    // …тут пакуємо й шлемо навігаційну команду (SET_POSITION_TARGET_*) рівно 5 Гц…
}
