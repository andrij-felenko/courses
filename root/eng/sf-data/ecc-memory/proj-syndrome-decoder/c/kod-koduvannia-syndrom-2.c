/* Синдром: XOR номерів усіх позицій, де стоїть 1.
   Для цілого слова = 0; для одного битка = номер битої позиції. */
static unsigned syndrome(word72 cw) {
    unsigned s = 0;
    for (unsigned p = 1; p < N; ++p)        /* позиція 0 (=0) у XOR нічого не додає */
        if ((cw >> p) & 1) s ^= p;
    return s;
}

/* Загальна парність: XOR усіх 72 бітів (0 = парна кількість одиниць). */
static unsigned parity(word72 cw) {
    unsigned g = 0;
    for (unsigned p = 0; p < N; ++p)
        g ^= (unsigned)((cw >> p) & 1);
    return g;
}
