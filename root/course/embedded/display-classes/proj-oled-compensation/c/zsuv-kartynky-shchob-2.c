// псевдовипадковий крок зсуву: нова ціль близько до старої, але в межах поля
static uint32_t rng_state = 0x2545F491u;
static uint32_t xorshift(void) {           // дешевий генератор для не-крипто задач
    rng_state ^= rng_state << 13;
    rng_state ^= rng_state >> 17;
    rng_state ^= rng_state << 5;
    return rng_state;
}
static void shift_random_step(disp_guard_t *g) {
    int s = g->shift_span;
    if (s == 0) return;
    // зсув на -1/0/+1 по кожній осі, із затиском у поле
    int dx = (int)(xorshift() % 3) - 1;
    int dy = (int)(xorshift() % 3) - 1;
    int x = g->shift_x + dx, y = g->shift_y + dy;
    if (x >  s) x =  s; if (x < -s) x = -s;
    if (y >  s) y =  s; if (y < -s) y = -s;
    g->shift_x = (int8_t)x;
    g->shift_y = (int8_t)y;
}
