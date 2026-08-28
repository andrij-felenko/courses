// Монітор слухає удари від вузла. Три пропущені підряд = вузол мертвий.
// Тактика купує ВИЯВЛЕННЯ (дізнаємось про смерть за ~1.5 с, а не від
// розлюченого користувача), але платить ТРАФІКОМ і РИЗИКОМ хибної тривоги.
constexpr uint32_t BEAT_PERIOD_MS = 500;   // як часто вузол має битися
constexpr int      MISS_LIMIT     = 3;     // скільки пропусків терпимо до вироку

struct Monitor {
    uint32_t last_beat_ms = 0;  // коли прийшов останній удар
    int      missed       = 0;  // скільки періодів поспіль тиша
    bool     alive        = true;  // наш поточний присуд про вузол
};

// Викликається раз на BEAT_PERIOD_MS з таймера монітора.
void monitor_tick(Monitor &m, uint32_t now_ms) {
    if (now_ms - m.last_beat_ms < BEAT_PERIOD_MS)
        return;                            // удар устиг — усе гаразд

    m.missed++;                            // період минув, а удару не було
    if (m.missed >= MISS_LIMIT && m.alive) {
        m.alive = false;                   // вирок: вузол мертвий
        on_node_down();                    // штовхаємо родину оговтання
    }
}

// Викликається, коли фізично прийшов удар від вузла.
void monitor_on_beat(Monitor &m, uint32_t now_ms) {
    m.last_beat_ms = now_ms;
    m.missed = 0;                          // тиша скинута — вузол живий
    m.alive = true;
}
