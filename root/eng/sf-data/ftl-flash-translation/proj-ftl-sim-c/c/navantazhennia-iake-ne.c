static uint32_t rng;
static uint32_t rnd(void) {          // xorshift32 — щоб прогін відтворювався
    uint32_t x = rng;
    x ^= x << 13; x ^= x >> 17; x ^= x << 5;
    return rng = x;
}

// hot_share % записів б'ють у перші hot_frac % адрес.
static uint32_t pick_lpn(uint32_t hot_share, uint32_t hot_frac) {
    if (hot_share && rnd() % 100 < hot_share)
        return rnd() % (nlog * hot_frac / 100);
    return rnd() % nlog;
}

static void ftl_init(uint32_t logical_pages) {
    nlog = logical_pages;
    memset(pstate, P_FREE, sizeof pstate);
    memset(invalid_cnt, 0, sizeof invalid_cnt);
    memset(erase_cnt, 0, sizeof erase_cnt);
    for (uint32_t i = 0; i < nlog; i++) map[i] = NONE;
    freetop = 0;
    for (uint32_t b = NBLK; b-- > 1; ) push_free(b);   // блок 0 — під фронт
    wblk = 0; wpage = 0;
    host_w = flash_w = erases = gc_copies = 0;
}
