static void run_case(const char *name, uint32_t op_pct,
                     uint32_t hot_share, uint32_t hot_frac) {
    uint32_t logical = (uint32_t)((uint64_t)NPHYS * 100 / (100 + op_pct));
    rng = 2463534242u;
    ftl_init(logical);

    for (uint32_t i = 0; i < logical; i++)          // 1. заповнити диск ущерть
        ftl_write(i, NULL);
    for (uint32_t i = 0; i < 4 * logical; i++)      // 2. прогріти до усталеного режиму
        ftl_write(pick_lpn(hot_share, hot_frac), NULL);

    host_w = flash_w = erases = gc_copies = 0;      // 3. і ТІЛЬКИ ТЕПЕР міряти
    for (uint32_t i = 0; i < 10 * logical; i++)
        ftl_write(pick_lpn(hot_share, hot_frac), NULL);

    uint32_t emin = 0xFFFFFFFFu, emax = 0, never = 0;
    for (uint32_t b = 0; b < NBLK; b++) {
        if (erase_cnt[b] == 0) { never++; continue; }
        if (erase_cnt[b] < emin) emin = erase_cnt[b];
        if (erase_cnt[b] > emax) emax = erase_cnt[b];
    }
    printf("OP=%3u%%  WA=%5.2f  копій=%8llu  стирань=%6llu"
           "  знос %3u…%3u  поза обігом: %u   %s\n",
           op_pct, (double)flash_w / (double)host_w,
           (unsigned long long)gc_copies, (unsigned long long)erases,
           emin, emax, never, name);
}

int main(void) {
    run_case("рівномірне випадкове",     100, 0, 0);
    run_case("рівномірне випадкове",      50, 0, 0);
    run_case("рівномірне випадкове",      28, 0, 0);
    run_case("рівномірне випадкове",       7, 0, 0);
    run_case("90 % записів у 10 % адрес", 28, 90, 10);
    run_case("90 % записів у 10 % адрес",  7, 90, 10);
    return 0;
}
