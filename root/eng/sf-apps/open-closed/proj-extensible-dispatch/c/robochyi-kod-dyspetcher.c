// Параметри окремих знижок — кожна знає лише свою структуру.
typedef struct { int percent; }          PercentParams;   // −percent%
typedef struct { long amount; }          FlatParams;      // −amount копійок
typedef struct { int percent; long cap; } LoyaltyParams;  // −percent%, але не більше cap

static long disc_percent(long total, const void *p) {
    const PercentParams *pp = (const PercentParams *)p;    // розтлумачив своє
    return total * pp->percent / 100;
}

static long disc_flat(long total, const void *p) {
    (void)total;                                           // фіксованій сума кошика байдужа
    const FlatParams *fp = (const FlatParams *)p;
    return fp->amount;
}

static long disc_loyalty(long total, const void *p) {
    const LoyaltyParams *lp = (const LoyaltyParams *)p;
    long d = total * lp->percent / 100;
    return d < lp->cap ? d : lp->cap;                      // обмежили стелею
}
