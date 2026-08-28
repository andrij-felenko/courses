// Бік СПОЖИВАЧА подій (напр. місток дому). Відкидає дублікати за seq.
static uint32_t g_last_seq_seen = 0;

static void on_event_received(uint32_t seq, uint8_t type,
                              uint32_t ts, const char *data) {
    if (seq <= g_last_seq_seen) {
        // Уже бачили цей номер (або старіший) — це повтор від QoS 1. Ігноруємо.
        return;
    }
    g_last_seq_seen = seq;
    handle_event(type, ts, data);      // ось тут — реальна реакція на подію
}
