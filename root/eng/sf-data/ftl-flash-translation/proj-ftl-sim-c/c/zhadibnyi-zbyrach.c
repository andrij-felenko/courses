// Жертва — блок із найбільшим числом недійсних сторінок.
static uint32_t pick_victim(void) {
    uint32_t best = NONE, best_inv = 0;
    for (uint32_t b = 0; b < NBLK; b++)
        if (b != wblk && invalid_cnt[b] > best_inv) {
            best = b; best_inv = invalid_cnt[b];
        }
    return best;
}

static void gc_run(void) {
    uint32_t v = pick_victim();
    if (v == NONE) {
        fprintf(stderr, "FTL: нема чого збирати — диск справді повний\n");
        exit(1);
    }
    for (uint32_t i = 0; i < PPB; i++) {        // рятуємо чинні сторінки
        uint32_t ppn = v * PPB + i;
        if (pstate[ppn] != P_VALID) continue;
        uint32_t lpn = powner[ppn];             // OOB каже, чий це LPN
        uint32_t dst = alloc_page();
        pstate[dst] = P_VALID;
        powner[dst] = lpn;
        map[lpn] = dst;                         // карта — на копію
        flash_w++; gc_copies++;                 // запис, якого хост НЕ просив
    }
    for (uint32_t i = 0; i < PPB; i++)          // стирання — цілим блоком
        pstate[v * PPB + i] = P_FREE;
    invalid_cnt[v] = 0;
    erase_cnt[v]++;
    erases++;
    push_free(v);                               // блок назад у пул
}
