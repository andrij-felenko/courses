/* C: побітова перевірка (rand & 3 == 0) дає ймовірність 1/4 за 1 такт */
static uint32_t xorshift32_state = 2463534242U;
static uint32_t fast_rand(void) {
    uint32_t x = xorshift32_state;
    x ^= x << 13;
    x ^= x >> 17;
    x ^= x << 5;
    xorshift32_state = x;
    return x;
}

static int random_level(void) {
    int lvl = 1;
    while ((fast_rand() & 3) == 0 && lvl < SKIPLIST_MAX_LEVEL) {
        lvl++;
    }
    return lvl;
}
