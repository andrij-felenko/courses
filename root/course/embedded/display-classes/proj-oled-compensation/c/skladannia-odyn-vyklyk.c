// викликати раз на кадр: оновити весь стан захисту й застосувати важелі до панелі
void disp_guard_tick(disp_guard_t *g, uint32_t now_ms,
                     uint8_t avg_r, uint8_t avg_g, uint8_t avg_b,
                     uint16_t max_code) {
    // 1) знос: інтегруємо світло каналів за час від минулого тіку
    static uint32_t prev_ms = 0;
    uint32_t dt = prev_ms ? (now_ms - prev_ms) : 0;
    prev_ms = now_ms;
    if (dt) wear_accumulate(g, avg_r, avg_g, avg_b, dt);

    // 2) згасання: час бездіяльності -> ціль яскравості
    idle_update_target(g, now_ms);

    // 3) яскравість: один плавний крок до цілі + переклад у код панелі
    bright_slew(g, 20 /* крок/кадр у перцептивних одиницях */);
    uint16_t panel_code = perc_to_panel(g->bright_now, max_code);
    panel_set_brightness(panel_code);            // одна команда в драйвер

    // 4) зсув: якщо настав час — один крок орбіти
    if (now_ms - g->last_shift_ms >= g->shift_period_ms) {
        g->last_shift_ms = now_ms;
        shift_random_step(g);
        panel_set_scroll(g->shift_x, g->shift_y); // або зсув вікна малювання
    }

    // 5) синій за зносом — масштаб для малювального коду (він застосує плавно)
    g->blue_scale = wear_blue_scale(g);
}
