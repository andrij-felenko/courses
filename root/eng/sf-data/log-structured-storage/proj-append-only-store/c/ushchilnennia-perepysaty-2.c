// Який журнал активний? Той, чия печатка-покоління ДІЙСНА й НАЙБІЛЬША.
// Жодної дійсної печатки нема (незайманий чіп) → беремо A за замовчуванням.
static uint32_t read_active(uint32_t *out_gen) {
    seal_t a, b;
    flash_read(SEAL_OFF(LOG_A), &a, sizeof a);
    flash_read(SEAL_OFF(LOG_B), &b, sizeof b);
    int va = seal_valid(&a), vb = seal_valid(&b);

    if (va && (!vb || a.generation >= b.generation)) { *out_gen = a.generation; return LOG_A; }
    if (vb)                                          { *out_gen = b.generation; return LOG_B; }
    *out_gen = 0;                                     // ще жодного ущільнення → перший журнал
    return LOG_A;
}
