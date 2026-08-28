// один крок зсуву по прямокутній орбіті в межах [-span, +span]
// обходимо периметр квадрата span×span за 8·span кроків
static void shift_orbit_step(disp_guard_t *g) {
    int s = g->shift_span;
    if (s == 0) return;
    int x = g->shift_x, y = g->shift_y;
    // рух за годинниковою: вниз по правій, вліво по нижній, вгору по лівій, вправо по верхній
    if      (x ==  s && y <  s) y++;      // права грань: вниз
    else if (y ==  s && x > -s) x--;      // нижня грань: вліво
    else if (x == -s && y > -s) y--;      // ліва грань: вгору
    else                        x++;      // верхня грань: вправо (і старт)
    g->shift_x = (int8_t)x;
    g->shift_y = (int8_t)y;
}
