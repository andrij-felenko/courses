// Абсолютний час початку вікна k у поточному (чи наступному) кадрі.
static uint64_t slot_start_time(uint8_t k) {
    uint64_t now        = now_us();
    uint64_t since      = now - g_epoch_us;
    uint64_t frame_no   = since / FRAME_US;          // який кадр іде
    uint64_t this_frame = g_epoch_us + frame_no * FRAME_US;
    uint64_t t          = this_frame + (uint64_t)k * SLOT_US;
    if (t <= now) t += FRAME_US;                      // це вікно вже минуло — беремо наступний кадр
    return t;
}

// Звести апаратний таймер-компаратор на абсолютний момент t (мкс).
static void arm_timer_at(uint64_t t);                // платформозалежне
