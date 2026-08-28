// Один такт бек-енду. Приймає свіжі сирі цифри raw[0..NSTAGE-1] і 2-бітний хвіст final2.
// Коли конвеєр наповнився — кладе у *out зібраний код відліку, що зайшов LAT тактів тому.
// Повертає 1, якщо код дійсний (конвеєр уже примінений), інакше 0 (ще наповнюється).
static int be_step(backend_t *b, const uint8_t raw[NSTAGE], uint8_t final2, uint16_t *out) {
    const int L = NSTAGE;                              // довжина кільця

    for (int s = 0; s < NSTAGE; ++s)                  // (1) записати свіжі цифри
        b->line[s][b->wr] = raw[s] & 0x3;             //     (лише 2 біти цифри)
    b->fin[b->wr] = final2 & 0x3;

    int valid = (b->filled >= LAT);                   // конвеєр наповнився?
    if (valid) {                                      // (2) вирівняти й скласти
        uint16_t code = 0;
        for (int s = 0; s < NSTAGE; ++s) {
            int delay = LAT - s;                      // щабель 0 → 5 тактів, … щабель 5 → 0
            int idx   = ((b->wr - delay) % L + L) % L;// зчитати з глибини кільця
            uint8_t d = b->line[s][idx];              // цифра цього щабля для ОДНОГО відліку
            code += (uint16_t)d << ((NBITS - 2) - s); // вага: 6,5,4,3,2,1 — зсув на 1 розряд/щабель
        }
        code += (uint16_t)b->fin[b->wr];              // хвіст-flash у два молодші розряди
        uint16_t max_code = (uint16_t)((1u << NBITS) - 1);
        if (code > max_code) code = max_code;         // страховка від переповнення на краю
        *out = code;
    }

    b->wr = (b->wr + 1) % L;                          // (3) посунути кільце
    if (b->filled <= LAT) b->filled++;
    return valid;
}
