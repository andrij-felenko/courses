// один крок зближення поточної яскравості з ціллю; повертає true, якщо ще рухаємось
static bool bright_slew(disp_guard_t *g, uint16_t step_per_frame) {
    if (g->bright_now == g->bright_target) return false;
    if (g->bright_now < g->bright_target) {
        g->bright_now += step_per_frame;
        if (g->bright_now > g->bright_target) g->bright_now = g->bright_target; // не перелетіти
    } else {
        // на спаді крок робимо трохи меншим: темніти приємніше повільно
        uint16_t s = step_per_frame > 1 ? step_per_frame - 1 : 1;
        g->bright_now = (g->bright_now > s) ? g->bright_now - s : 0;
        if (g->bright_now < g->bright_target) g->bright_now = g->bright_target;
    }
    return true;
}
